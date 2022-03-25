#!/usr/bin/env python2

""" Parses the historical poker data
Modes
- Torneos: %d | Mesas Totales: %d
  + Sorted By Puntos x Mesa
- Podios y Puestos Totales 
  + By Primero
  + By Podios
  + By Ultimo
- Rivalidades - Heads Up (2 o mas)

"""

import os
import sys
import argparse
import csv
import datetime
from collections import defaultdict
import collections
import re
import codecs
import glob
import time


############## CLASSES ##############
class Jugador(object):	
#	def __init__(self, nombre):
#		self.nombre = nombre
	
	def __init__(self, nombre="", puntos=None, pj=0, roi=0, billete=0):
		self.nombre = nombre
		self.puntos = puntos
		self.pj = pj
		self.roi = roi
		self.billete = billete
		
	def __str__(self):
		#return f'Jugador({self.nombre}, {self.puntos})'
		printStr= 'Jugador (['+ self.nombre + '], Puntos ['+ str(self.puntos) +'])'
		return printStr

		
class JugadorStats(Jugador):
	def __init__(self):
		super(Jugador, self).__init__()
		self.pjPorcentaje= 0.0
		self.roiTotal= 0.0
		self.ptsPorMesa= 0.0
		self.primeroCnt= 0
		self.segundoCnt= 0
		self.terceroCnt= 0
		self.penultimoCnt= 0
		self.ultimoCnt= 0
		self.podioCnt= 0
		
		
	def __init__(self, nombre, puntos, pj, roi, billete):
		super(Jugador, self).__init__()
		self.nombre = nombre
		self.puntos = puntos
		self.pj = pj
		self.roi = roi
		self.billete = billete
		self.pjPorcentaje= 0.0
		self.roiTotal= 0.0
		self.ptsPorMesa= 0.0
		self.primeroCnt= 0
		self.segundoCnt= 0
		self.terceroCnt= 0
		self.penultimoCnt= 0
		self.ultimoCnt= 0
		self.podioCnt= 0
	
		
class Mesa:
	def __init__(self, dateStr="01/01/01" , jugadores=None):
		self.date = datetime.datetime.strptime(dateStr, "%m/%d/%y")
		self.jugadores= []
		self.podio= Podio()
		self.headsUp= HeadsUp()
		self.penultimo= None
		self.penultCampPos= None
		self.ultimo= None
		self.ultCampPos= None
		
	def __str__(self):		
		printStr= 'Mesa(Fecha [' + self.date.strftime("%m/%d/%y") + '], ' + str(self.podio) + ', Ultimo ['+ str(self.ultimo)
		if(self.penultimo):
			printStr += '], Penultimo [' + str(self.penultimo)
		printStr += '])'
		return printStr	
		
class Campeonato:
	def __init__(self, name, begDateStr="01/01/01", endStr="01/01/01"):
		self.name= name
		self.begDate = datetime.datetime.strptime(begDateStr, "%m/%d/%y")
		self.endDate= datetime.datetime.strptime(endStr, "%m/%d/%y")
		self.jugadores= []
		#sample: [[1, JugadorX], [2, JugadorY]]
		self.poss= defaultdict(list)
		#sample: [["4/29/20", MesaX], ["5/8/20", MesaY]]
		self.mesas= defaultdict(list)
		
class Podio:
	def __init__(self):
		self.primero= None
		self.segundo= None
		self.tercero= None
		
	def __str__(self):
		printStr= "Podio(Primero [" + str(self.primero) + "], Segundo [" + str(self.segundo) + "], Tercero [" + str(self.tercero) + "])"
		return printStr
		
	def sortedPodioStr(self):
		lst= []
		lst.append(self.primero)
		lst.append(self.segundo)
		lst.append(self.tercero)
		lst.sort()
		retStr= ""
		for x in lst:
			retStr += str(x) + ', ';
		
		last_char_index = retStr.rfind(', ')
		retStr= retStr[:last_char_index]
		return retStr
		
class HeadsUp:
	def __init__(self):
		self.primero= None
		self.segundo= None
		
	def __str__(self):
		printStr= "HeadsUp(Primero [" + str(self.primero) + "], Segundo [" + str(self.segundo) + "]"
		return printStr
		
	def sortedHeadsUpStr(self):
		lst= []
		lst.append(self.primero)
		lst.append(self.segundo)
		lst.sort()
		retStr= ""
		for x in lst:
			retStr += str(x) + ' vs ';
		
		last_char_index = retStr.rfind(' vs ')
		retStr= retStr[:last_char_index]
		return retStr
		
class Estadisticas:
	def __init__(self, campTot=0):
		self.campTot= campTot
		self.mesasTot= 0
		#sample ["Pomp", JugadorStats]
		self.jugsDict= {}
		self.primeros= {}
		self.segundos= {}
		self.terceros= {}
		self.jugsWithPoss= {}
		self.podDict= {}
		self.huDict= {}
		
class PodioStats:
	def __init__(self):
		self.jugsStr= None
		self.cnt= 0
		self.primeros= {}
		self.segundos= {}
		self.terceros= {}
		
	def __str__(self):
		printStr= "[Primeros] "
		for x in self.primeros:
			printStr = printStr + str(x) + ": " + str(self.primeros.get(x)) + " "
			
		printStr += " [Segundos] "
		for x in self.segundos:
			printStr = printStr + str(x) + ": " + str(self.segundos.get(x)) + " "
			
		printStr += " [Terceros] "
		for x in self.terceros:
			printStr = printStr + str(x) + ": " + str(self.terceros.get(x)) + " "
	
		return printStr
		

class HeadsUpStats:
	def __init__(self):
		self.jugsStr= None
		self.cnt= 0
		self.primeros= {}
		self.segundos= {}
		
	
	def __str__(self):
		#[Ganados] Bru: 3, Lilo: 2 
		printStr= "[Ganados] "
		for x in self.primeros:
			printStr= printStr + str(x) + ": " +  str(self.primeros.get(x)) + ", "
			
		last_char_index = printStr.rfind(', ')
		printStr= printStr[:last_char_index]
			
		return printStr	
		
	def sortPrimeros(self):
		self.primeros=  collections.OrderedDict(reversed(sorted(
			self.primeros.items(),
			key=lambda x: x[1]
		)))
	
	
	def strFull(self):
		printStr= "[Primeros] "
		for x in self.primeros:
			printStr = printStr + str(x) + ": " + str(self.primeros.get(x)) + " "
			
		printStr += " [Segundos] "
		for x in self.segundos:
			printStr = printStr + str(x) + ": " + str(self.segundos.get(x)) + " "
		
		return printStr	
		
class Logger(object):
    def __init__(self):
		self.terminal = sys.stdout
		timestr = time.strftime("%Y%m%d")
		self.log = open("papada-resultados-" + timestr + ".log", "w")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

		

# HELPER METHODS
def quit():
	"""Program was not initialized correctly"""
	print("example: python parsePokerData.py -d torneos")
	sys.exit(1)


def custom_error(message):
	"""Some other custom error"""
	print("There is a problem: %s" % message)
	sys.exit(2)
	
def getInputOrDefault(inputVal, default):
	if not inputVal:
		#print ("returning " + default)
		return default
	
	else:
		#print ("returning ", inputVal)
		return inputVal
		
def toInt(s):
	try:
		i = int(s)
	except ValueError:
		i = None
	return i
	
def toFloat(s):
	try:
		i = float(s)
	except ValueError:
		i = 0
	return i
	
#expects an string formatted like: int%
def toRoi(s):
	#remove %
	myStr= str(s).replace("%", "")
	return toInt(myStr)
    
def sort_dict_by_date(the_dict, date_format):
    # Python dicts do not hold their ordering so we need to make it an
    # ordered dict, after sorting.
    return collections.OrderedDict(sorted(
            the_dict.items(),
            key=lambda x: datetime.datetime.strptime(x[0], date_format)
        ))
        
def calcPerc(totNum, smallNum):
	#print (totNum, smallNum, round((smallNum*100)/totNum))
	#return round((smallNum*100)/totNum)
	return (smallNum*100)/totNum
	
###### Printing Methods ######

#Prints the main table sorted by puntosXmesa
def printMainTable(stats):
	print (" Torneos: %d | Mesas Totales: %d" % (stats.campTot, stats.mesasTot))
	#print (" Torneos: %d | Mesas Totales: %d (2 anos 1 dia)" % (stats.campTot, stats.mesasTot))
	print "----------------------------------------------"
        
    #sort jugsDict by puntos x Mesa
	stats.jugsDict= collections.OrderedDict(reversed(sorted(
			stats.jugsDict.items(),
			key=lambda x: float(x[1].ptsPorMesa)
#			key=lambda x: float(x[1].puntos)
		)))
	
	for idx, x in enumerate(stats.jugsDict):
	#for x in stats.jugsDict:		
		#for desktop/iPad
		print ("%s.[%s] Pts/Mesa: %s | Pts: %s | MJ: %s (%s%%) | $$: %s | ROI: %s%%" % (str(idx+1).rjust(2), x.ljust(8), str(round(stats.jugsDict[x].ptsPorMesa, 2)).ljust(4), 
				str(stats.jugsDict[x].puntos).ljust(3), str(stats.jugsDict[x].pj).ljust(2), str(stats.jugsDict[x].pjPorcentaje).rjust(2), 
				str(round(float(stats.jugsDict[x].billete), 2)).ljust(6), str(int(stats.jugsDict[x].roiTotal)).rjust(3)))

	print "\n----------------------------------------------"

##### PRINT PODIOS Y PUESTOS #####
def printPodiosPuestos(stats):
	for idx, x in enumerate(stats.jugsDict):
		mj= int(stats.jugsDict[x].pj)
	
		#print (x, "Pods:" , stats.jugsDict[x].podiosCnt, "Prim: ", stats.jugsDict[x].primeroCnt, "Seg: ", stats.jugsDict[x].segundoCnt, "Ter: ", stats.jugsDict[x].terceroCnt, "Penul: ", stats.jugsDict[x].penultimoCnt, "Ult: ", stats.jugsDict[x].ultimoCnt)
		print("%s.[%s] | Podios: %s (%s%%)| 1ro: %s (%s%%)| 2do: %s (%s%%)| 3ro: %s (%s%%)| Penul: %s (%s%%)| Ult: %s (%s%%)" % (str(idx+1).rjust(2), x.ljust(8), 
			str(stats.jugsDict[x].podiosCnt).rjust(2), str(calcPerc(mj, stats.jugsDict[x].podiosCnt)).rjust(2), str(stats.jugsDict[x].primeroCnt).rjust(2), 
			str(calcPerc(mj, stats.jugsDict[x].primeroCnt)).rjust(2), str(stats.jugsDict[x].segundoCnt).rjust(2), str(calcPerc(mj, stats.jugsDict[x].segundoCnt)).rjust(2),
			str(stats.jugsDict[x].terceroCnt).rjust(2), str(calcPerc(mj, stats.jugsDict[x].terceroCnt)).rjust(2), stats.jugsDict[x].penultimoCnt, 
			str(calcPerc(mj, stats.jugsDict[x].penultimoCnt)), str(stats.jugsDict[x].ultimoCnt).rjust(2),  str(calcPerc(mj, stats.jugsDict[x].ultimoCnt)).rjust(2)))

	print "\n----------------------------------------------"
	
##### HEADS UP / RIVALIDADES #####
def printRivalidades(stats):
	stats.huDict= collections.OrderedDict(reversed(sorted(
			stats.huDict.items(),
			key=lambda x: float(x[1].cnt)
		)))
		
	print (" Rivalidates - Heads Up (2 o mas)")
	print "----------------------------------------------"
	totHeadsUp= 0
	for idx, x in enumerate(stats.huDict):
		stats.huDict[x].sortPrimeros()
		if(stats.huDict[x].cnt > 1):
			print("[%s] Heads Up: %d | %s" % (stats.huDict[x].jugsStr.rjust(17), stats.huDict[x].cnt, str(stats.huDict[x])))
		
		totHeadsUp += stats.huDict[x].cnt
#	print ("TOT HEADS UP", totHeadsUp)	
	print "\n----------------------------------------------"	


############## MAIN ##############
if __name__ == "__main__":
	begin_time = datetime.datetime.now()
	#initialize logger for console and file output
	sys.stdout = Logger()
	print ("\n=================== PArsePAkerDAta.py (PAPADA) - Ejecutando ====================\n")
	#GLOBAL VARS
	defaultinDir= "torneos"
	campeonatos= []
	costoMesa= 5

	#########################################################################################
	""" Process command line arguments """
	# Parse and process command line args
	parser = argparse.ArgumentParser(description='PArsePAkerDAta.py (PAPADA) - Procesa e imprime las estadisticas de los Campeonatos de Poker')
	parser.add_argument('-d', '--inDir', help='Directorio con todos los archivos CSV')
	parser.add_argument('-pd', '--podios', action='store_true', help='Imprimir Puestos y Podios - Ordenados x Podios')
	parser.add_argument('-pp', '--podiosPrim', action='store_true', help='Imprimir Puestos y Podios - Ordenados x Primeros Puestos')
	parser.add_argument('-pu', '--podiosUlt', action='store_true', help='Imprimir Puestos y Podios - Ordenados x Ultimos Puestos')
	parser.add_argument('-r', '--rivalidades', action='store_true', help='Imprimir Rivalidades - Heads Up (2 o mas)')

	# Call custom function for additional console output when parse fails
	try:
		args = parser.parse_args()
	except SystemExit:
		quit()

	# Assign command line args to variables
	#inDir = args.inDir
	inDir= getInputOrDefault(args.inDir, defaultinDir)

	#print inDir
	
	#rows = []
	#csvReader = csv.reader(codecs.open('torneos/torneo1.csv', 'rU', 'utf-8'))
	#fields = next(csvReader)
	#for row in csvReader:
	#	rows.append(row)
	#print "OPENED"
	
	csvDir= os.path.join(os.getcwd(), inDir)	
	for idx, filename in enumerate(glob.glob(csvDir + "/*.csv")):
		jugs= []
		
		with open(os.path.join(csvDir, filename), 'r') as csvfile: # open in readonly mode
		#with codecs.open('torneos/torneo1.csv', 'r', 'utf-8') as csvfile: # open in readonly mode
			#print ("Processing", os.path.join(csvDir, filename))
		
      		# do your stuff
			#########################################################################################
			""" Read CSV file """
			# initializing the titles and rows list
			fields = []
			rows = []
	
			# creating a csv reader object
			csvreader = csv.reader(csvfile)
	
			# extracting field names through first row
			fields = next(csvreader)
	  
			# extracting each data row one by one
			for row in csvreader:
				rows.append(row)
		
		#process torney files
		#Indexes = CSV structure
		posIdx=0
		nombreIdx= 1
		begMesaIdx= 2
		ultMesaIdx= len(fields)-5
		pjIdx= len(fields)-4
		puntosIdx= len(fields)-3
		billIdx= len(fields)-2
		roiIdx= len(fields)-1
		
		#initialize Campeonato
		ultMesaIdx= len(fields)-5
		
		#filename format MUST BE anyString11.anyting
		campRegex= re.compile(r'(\d+).')
		mo= campRegex.search(filename)
		
		currCampName= "Torneo " + mo.group(1)
		currCamp= Campeonato(currCampName, fields[begMesaIdx], fields[ultMesaIdx])
		
		#initialize possDict
		possDict= defaultdict(list)
		mesasDict= defaultdict(list)
		
		#create mesas based on the dates in fields[] between idx=2 and idx= len(fields)-4
		#sample: [["4/29/20", MesaX], ["5/8/20", MesaY]]
		#self.mesas= defaultdict(list)
		for i in range(2, len(fields)-4):
			currMesa= Mesa(fields[i])
			mesasDict[fields[i]].append(currMesa)
		
		jugsMesa= []
		#process jugadores and add data to mesas
		for j, row in enumerate(rows):
			#process jugador
			currJug= Jugador(row[nombreIdx], row[puntosIdx], row[pjIdx], row[roiIdx], row[billIdx])
			jugs.append(currJug)			
			
			#add data to possDict
			#sample: [[1, JugadorX], [2, JugadorY]]
			possDict[int(row[posIdx])].append(currJug)

			#add data to mesas
			#loop to go through each mesa data for player
			#print ("------- NEW PLAYER ---------")
			for i in range(2, len(fields)-4):
				#get currMesa, currPodio, currHeadsUp
				currMesa= mesasDict[fields[i]][0]
				currPodio= currMesa.podio
				currHeadsUp= currMesa.headsUp
				#initialize currJugMesa
				currJugMesa= Jugador(row[nombreIdx])
						
				#check points val and update mesa
				pts= toInt(row[i])
				#print ("Nombre: ", row[nombreIdx], ", Pts: ",  pts)
				if(pts == 5):
					currPodio.primero= row[nombreIdx]
					currHeadsUp.primero= row[nombreIdx]
					currJugMesa.puntos= pts
					
				elif(pts == 3):
					currPodio.segundo= row[nombreIdx]
					currHeadsUp.segundo= row[nombreIdx]
					currJugMesa.puntos= pts					
					
				elif(pts == 1):
					if(currPodio is not None):
						currPodio.tercero= row[nombreIdx]
					if(currHeadsUp is not None):
						currHeadsUp.tercero= row[nombreIdx]
					currJugMesa.puntos= pts	
				
				#first and second split case. Cannot count podio or heads up
				elif (pts == 4):
					currMesa.podio= None
					currMesa.headsUp= None
					currJugMesa.puntos= pts
				
				#process puntos negativos
				elif(pts != None and pts < 0):
					#print ("INSIDE - Nombre: ", row[nombreIdx], ", Pts: ",  pts)
					currJugMesa.puntos= pts
					#solo primer campeonato tiene -3
					if currCampName == 'Torneo 1':
						if (pts == -3):
							currMesa.ultimo= row[nombreIdx]
							currMesa.ultCampPos= row[posIdx]
						elif (pts == -1):
							currMesa.penultimo= row[nombreIdx]
							currMesa.penultCampPos= row[posIdx]
					else:
						#use case1: dos -1, ya vi uno
						#if already there is an ultimo then ultimo is the one w the least points
						if(currMesa.ultimo):
							#print ("INSIDE currRow - Nombre: ", row[nombreIdx], ", Pts: ",  pts, ", Pos: ", row[posIdx])
							#print ("currMesa.ultimo - Nombre: ", currMesa.ultimo, ", Pos: ",  currMesa.ultCampPos)
							if int(currMesa.ultCampPos) < int(row[posIdx]):
								#swap
								#print ("Swapping")
								currMesa.penultimo= currMesa.ultimo
								currMesa.penultCampPos= currMesa.ultCampPos
								currMesa.ultimo= row[nombreIdx]
								currMesa.ultCampPos= row[posIdx]
							else:
								#add current row as penultimo
								currMesa.penultimo= row[nombreIdx]
								currMesa.penultCampPos= row[posIdx]
						
						#use case2: solo uno -1, primero q veo
						else:						
							currMesa.ultimo= row[nombreIdx]
							currMesa.ultCampPos= row[posIdx]
						
				else:
					currJugMesa.puntos= pts
	
				#add only if Jugador jugo la mesa			
				if(currJugMesa.puntos != None):
					currMesa.jugadores.append(currJugMesa)
				#END for each mesa for jugador row			
			
			#END going through all rows
				
		collections.OrderedDict(sorted(possDict.items()))
		mesasDict= sort_dict_by_date(mesasDict, '%m/%d/%y')		
		currCamp.jugadores= jugs
		currCamp.poss= possDict
		currCamp.mesas= mesasDict
		
		campeonatos.append(currCamp)
		#END WITH/open csv file 
		
	#END FOR for csvFolder
	#END DATA INJESTION
	
	#CALCULATE STATS
	stats= Estadisticas(len(campeonatos))
	allBillDict= {}
	mesasTot= 0
	
	#HIGH LEVEL FLOW/LOGIC
	#for each camp
		#for each Jugador in camp.poss
			#initialize jugsStats
			#OR
			#update jugsStats
			
		#for each mesa in camp
			#process podio
			#add to stats: primero, segundo, tercero
			
			#process heads up
			#add to stats: primero, segundo
			
			#search based on podio.primero (segundo, tercero, penultimo, ultimo) and update record in jugsStats
			
		
	
	for camp in campeonatos:
		#print (camp.name)
		mesasTot += len(camp.mesas)
		
		for x in camp.poss:
			currJug= camp.poss[x][0];
			#print ("Pos [", x , "] Nombre [", currJug.nombre, '] Puntos [', currJug.puntos, '] PJ[', currJug.pj, '] ROI[', currJug.roi , '] Billete [', currJug.billete, ']')
				
			#create the stat record
			if(stats.jugsDict.get(currJug.nombre) is None):
				stats.jugsDict[currJug.nombre]= JugadorStats(currJug.nombre, currJug.puntos, currJug.pj, currJug.roi, currJug.billete)
				
			#aggregate the data
			else:
				myPts= int(stats.jugsDict[currJug.nombre].puntos)
				stats.jugsDict[currJug.nombre].puntos = myPts + int(currJug.puntos)
				myPj= int(stats.jugsDict[currJug.nombre].pj)
				stats.jugsDict[currJug.nombre].pj = myPj + int(currJug.pj)
				myRoi= toRoi(stats.jugsDict[currJug.nombre].roi)
				stats.jugsDict[currJug.nombre].roi = myRoi + toRoi(currJug.roi)
				myBill= toFloat(stats.jugsDict[currJug.nombre].billete)
				stats.jugsDict[currJug.nombre].billete= myBill + toFloat(currJug.billete)
			
		#print all data in mesas
		for mesa in camp.mesas:
			currMesa= camp.mesas[mesa][0]
			#print currMesa
			
			#search based on podio.primero (segundo, tercero, penultimo, ultimo) and update record in jugsStats
			#currJugStat= stats.jugsDict[currJug.nombre] - CANNOT USE THIS
			
#			if(stats.jugsDict.get(currMesa.ultimo)):
			jugStats= stats.jugsDict.get(currMesa.penultimo)
			if(jugStats):
				jugStats.penultimoCnt += 1
				
			jugStats2= stats.jugsDict.get(currMesa.ultimo)
			if(jugStats2):
				jugStats2.ultimoCnt += 1
			
			
			#process podio
			currPodio= currMesa.podio
			if (currPodio is None) or (currPodio.tercero is None):
				#print ("SKIPPING este podio")
				pass
			
			else: #process podio into PodioStats
				
				jugStats= stats.jugsDict.get(currPodio.tercero)
				if(jugStats):
					jugStats.terceroCnt += 1
				
				podStr= currPodio.sortedPodioStr()
				podioStats = None
			
				if(stats.podDict.get(podStr) is None):
					p= PodioStats()
					stats.podDict[podStr]= p
					podioStats= p
					podioStats.jugsStr= podStr
					podioStats.cnt= 1
				
				else:
					podioStats= stats.podDict[podStr]
					podioStats.cnt += 1			
			
				#primeros[  ["Pomp", 1], ["Bruno", 2]  ]
				#process primero			
				if(podioStats.primeros.get(currPodio.primero) is None):
					#new add it
					podioStats.primeros[currPodio.primero] = 1
					#print ("In primero IF", currPodio.primero, podioStats.primeros[currPodio.primero])
				
				else:
					#existing +1
					podioStats.primeros[currPodio.primero] += 1
					#print ("In primero ELSE", currPodio.primero, podioStats.primeros[currPodio.primero])
			
				#process segundo
				if(podioStats.segundos.get(currPodio.segundo) is None):
					#new add it
					podioStats.segundos[currPodio.segundo] = 1
					#print ("In segundo IF", currPodio.segundo, podioStats.segundos[currPodio.segundo])
				
				else:
					#existing +1
					podioStats.segundos[currPodio.segundo] += 1
					#print ("In segundo ELSE", currPodio.segundo, podioStats.segundos[currPodio.segundo])
			
				#process tercero
				if(podioStats.terceros.get(currPodio.tercero) is None):
					#new add it
					podioStats.terceros[currPodio.tercero] = 1
				
				else:
					#existing +1
					podioStats.terceros[currPodio.tercero] += 1
				
				#add record to dict
				if(stats.podDict.get(podioStats.jugsStr) is None):
					stats.podDict[podioStats.jugsStr] = podioStats

	
				if(stats.terceros.get(currPodio.tercero) is  None):
					stats.terceros[currPodio.tercero] = 1
				
				else:
					stats.terceros[currPodio.tercero] += 1
					
			#END else process podio into Podio Stats
	
			#process headsUp
			currHeadsUp= currMesa.headsUp
			if (currHeadsUp is None):
				#print ("SKIPPING este headsUp")
				pass
			
			else: #process headsUp into HeadsUpStats
			
				jugStats= stats.jugsDict.get(currHeadsUp.primero)
				jugStats.primeroCnt += 1
				
				stats.jugsDict.get(currHeadsUp.segundo).segundoCnt +=1
			
				headsUpStr= currHeadsUp.sortedHeadsUpStr()
				headsUpStats = None
			
				if(stats.huDict.get(headsUpStr) is None):
					hu= HeadsUpStats()
					stats.huDict[headsUpStr]= hu
					headsUpStats= hu
					headsUpStats.jugsStr= headsUpStr
					headsUpStats.cnt= 1
				
				else:
					headsUpStats= stats.huDict[headsUpStr]
					headsUpStats.cnt += 1	
					
				#process primero	
				#print("headsUpStats.primeros.get(currHeadsUp.primero)", str(headsUpStats.primeros.get(currHeadsUp.primero)))
				if(headsUpStats.primeros.get(currHeadsUp.primero) is None):
					#new add it
					headsUpStats.primeros[currHeadsUp.primero] = 1
				
				else:
					#existing +1
					headsUpStats.primeros[currHeadsUp.primero] += 1
			
				#process segundo
				if(headsUpStats.segundos.get(currHeadsUp.segundo) is None):
					#new add it
					headsUpStats.segundos[currHeadsUp.segundo] = 1
					#print ("In segundo IF", currHeadsUp.segundo, headsUpStats.segundos[currHeadsUp.segundo])
				
				else:
					#existing +1
					headsUpStats.segundos[currHeadsUp.segundo] += 1
					#print ("In segundo ELSE", currHeadsUp.segundo, headsUpStats.segundos[currHeadsUp.segundo])	
					
				#add record to dict
				if(stats.huDict.get(headsUpStats.jugsStr) is None):
					stats.huDict[headsUpStats.jugsStr] = headsUpStats
				
				#now add data to pocision dicts
				if(stats.primeros.get(currHeadsUp.primero) is  None):
					stats.primeros[currHeadsUp.primero] = 1
				
				else:
					stats.primeros[currHeadsUp.primero] += 1
				
				if(stats.segundos.get(currHeadsUp.segundo) is  None):
					stats.segundos[currHeadsUp.segundo] = 1
				
				else:
					stats.segundos[currHeadsUp.segundo] +=1
					#print (currHeadsUp.segundo, stats.segundos[currHeadsUp.segundo])

			#end else process headsUp into HeadsUpStats
			
			#for x in currMesa.jugadores:
			#	print x
			
		#print "\n----------------------------------------------"
		#end campeonatos for
	
	#stats after data aggregation	
	stats.mesasTot= mesasTot
	for jug in stats.jugsDict:		

		costoTotal= int(stats.jugsDict[jug].pj) * costoMesa
		billTotal= toFloat(stats.jugsDict[jug].billete)
		stats.jugsDict[jug].roiTotal= ((billTotal-costoTotal) * 100)/costoTotal
		
		pjInt= toInt(stats.jugsDict[jug].pj)
		stats.jugsDict[jug].pjPorcentaje= (pjInt*100)/mesasTot
		
		ptsFloat= toFloat(stats.jugsDict[jug].puntos)
		stats.jugsDict[jug].ptsPorMesa= ptsFloat/int(stats.jugsDict[jug].pj)
		
		js= stats.jugsDict[jug]
		js.podiosCnt = js.primeroCnt + js.segundoCnt + js.terceroCnt
		
	
	#call helper methods based on the mode
	printMainTable(stats)
        
    
	if(args.podios):
		stats.jugsDict= collections.OrderedDict(reversed(sorted(
				stats.jugsDict.items(),
				key=lambda x: x[1].podiosCnt
		)))
		print (" Podios y Puestos Totales - By Podios")
		print "----------------------------------------------"
		printPodiosPuestos(stats)
		
	if(args.podiosPrim):
		stats.jugsDict= collections.OrderedDict(reversed(sorted(
				stats.jugsDict.items(),
				key=lambda x: x[1].primeroCnt
		)))
		print (" Podios y Puestos Totales - By Primero")
		print "----------------------------------------------"
		printPodiosPuestos(stats)
		
	if(args.podiosUlt):
		stats.jugsDict= collections.OrderedDict(reversed(sorted(
				stats.jugsDict.items(),
				key=lambda x: x[1].ultimoCnt
		)))
		print (" Podios y Puestos Totales - By Ultimo")
		print "----------------------------------------------"
		printPodiosPuestos(stats)	
		
	if(args.rivalidades):
		printRivalidades(stats)
	


	stats.podDict= collections.OrderedDict(reversed(sorted(
			stats.podDict.items(),
			key=lambda x: float(x[1].cnt)
		)))
		
	totPodios= 0
#	for idx, x in enumerate(stats.podDict):
#		print(stats.podDict[x].jugsStr, stats.podDict[x].cnt, str(stats.podDict[x]))
#		totPodios += stats.podDict[x].cnt
		
#	print ("TOT PODIOS\n", totPodios)
#	print "\n----------------------------------------------"
	
	stats.primeros= collections.OrderedDict(reversed(sorted(
			stats.primeros.items(),
			key=lambda x: float(x[1])
		)))
		
	#for x in stats.primeros:
	#	print ("Primeros", x, stats.primeros[x])
		
	#print "\n----------------------------------------------"
		
	#for x in stats.segundos:
	#	print ("Segundos", x, stats.segundos[x])
		
	#print "\n----------------------------------------------"
		
	#for x in stats.terceros:
	#	print ("Terceros", x, stats.terceros[x])
		
	#print "\n----------------------------------------------"
	
	
	#########################################################################################
	
	totTime= datetime.datetime.now() - begin_time
	print ("\n======= PArsePAkerDAta.py (PAPADA) - Completado - Runtime: %.2f segundos =======\n" %totTime.total_seconds())
	
	
	
