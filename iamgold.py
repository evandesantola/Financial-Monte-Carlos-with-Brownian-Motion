import csv
import numpy as np
import math
from scipy import stats
import sys, getopt

DEFAULT_INPUT = "GoogleData.csv"
DEFAULT_DAYS =  (60)
DEFAULT_PATHS= 20
DEFAULT_GRANULARITY	= 100000

def getStockPrices(file):
	with open(file, 'rb') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		titles=["date", "open", "high", "low", "close", "volume", "adjClose"]
		data={}
		for row in spamreader:
			for i in xrange(len(titles)):
				if (titles[i]) not in data:
					data[titles[i]]=[]
				foo= ','.join(row)
				foo=foo.split(",")
				data[titles[i]].append(foo[i])
		for i in xrange(len(titles)):
			data[titles[i]]=(data[titles[i]])[1::]
	stockPrices=[float(i) for i in data["close"]] #check this...
	return stockPrices

def generateStockPrices(mostRecentPrice,  lazy, T, N, sigma, r, mean):
	stockPrices=[float(mostRecentPrice)]
	deltaT=T/float(N)
	normal=(np.random.normal(0, 1, N))
	counter=0
	random = normal[0]

#	print "simulating stock prices"
	for t_j in xrange(int(N)):
		random = normal[t_j]
		S_jNew= float((stockPrices[-1]))*math.exp((r-(sigma*sigma*0.5))*deltaT+(sigma*random*math.sqrt(deltaT)))
		if (S_jNew<0): S_jNew=0
		if lazy:
			stockPrices[0]=S_jNew
		else:
			stockPrices.append[S_jNew]
		counter+=1
	#rint stockPrices
	return stockPrices

def generateEuropeanCallPrices(lastPrice, strikePrice, T, N, sigma, r, mean, n):
	terminalPrices=[]
	eRT=math.exp(-1*r*T)
	for i in xrange(n):
		p=(generateStockPrices(lastPrice, True, T, N, sigma, r, mean)[-1])
		#print "p is " + str(p)
		terminalPrices.append(max(0.0, p-strikePrice))
	array=np.array(terminalPrices)
	#print "standard error is " + str(stats.sem(array))
	return (eRT/n)*np.sum(array)

def generateEuropeanPutPrices(lastPrice, strikePrice, T, N, sigma, r, mean, n):
	terminalPrices=[]
	eRT=math.exp(-1*r*T)
	for i in xrange(n):
		terminalPrices.append(max(0.0, strikePrice-generateStockPrices(lastPrice, True, T, N, sigma, r, mean)[-1]))
	#this loop isn't really necessary] but this is the way it is presented in slides	
	array=np.array(terminalPrices)
	#print "standard error is " + str(stats.sem(array))
	return (eRT/n)*np.sum(array)

def getDailyReturn(stockPriceList):
	dailyReturns=[]
	for i in xrange(len(stockPriceList)-1):
		dailyReturns.append((stockPriceList[i+1]-stockPriceList[i])/stockPriceList[i])
	return np.std(np.array(dailyReturns))


def main(argv):
   inputFile = DEFAULT_INPUT
   days = DEFAULT_DAYS
   n = DEFAULT_PATHS
   N = DEFAULT_GRANULARITY	
   strikePrice= -1
   r=0.02/365
   try:	
      opts, args = getopt.getopt(argv,"hitnNsr:o:",["help=", "inputFile=", "time=", "n=", "N=", "strikePrice=", "r="])
   except getopt.GetoptError as err:
      print 'Error: ecoPhysics.py -i <inputFile> -t <tradingDays> -N <N> -s <strikePrice> -n <NumberPaths> -r <dailyRate>'
      print str(err)  # will print something like "option -a not recognized"
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h", "--help"):
      	 print 'Help: ecoPhysics.py -i <inputFile> -t <tradingDays> -N <N> -s <strikePrice> -n <NumberPaths>'
         sys.exit()
      elif opt in ("-i", "--inputFile"):
         inputFile = arg
      elif opt in ("-t", "--tradingDays"):
      	 days= int(arg)
      elif opt in ("-n", "--NumberPaths"):
      	 n= int(arg)
      elif opt in ("-N", "--N"):
      	 N= int(arg)
      elif opt in ("-s", "--strikePrice"):
      	print "arg is: " +str(arg)
      	strikePrice=float(arg)
      elif opt in ("-r", "--dailyRate"):
      	 r=float(arg)
      else:
			print 'Invalid format.  Arguments should be of the form: ecoPhysics.py -i <inputFile> -t <tradingDays> -N <N> -s <strikePrice> -n <NumberPaths>'
			sys.exit()

   if (strikePrice==-1): 
   		print "Must input strike price.  For help please read the readme or type ecoPhysics.py -h"
   		sys.exit()
   print "Note that for the purposes of this program, I assume that a year is defined as 252 trading days (has no weekends, holidays, etc.)"
   print "Input file is ", inputFile
   print "Number of trading days is (T)", float(days)
   print "Strike price is", strikePrice
   print "N is", N
   print "Number of Paths is", n
   print "Daily risk free rate is", r


   S=getStockPrices(inputFile)
   print "Current price is ", S[-1]

   volatility= getDailyReturn(S)#*math.sqrt(252)
   print "Daily volatility is: ", volatility
   print "Calculating call price.  If n or N is large this could take a while...\n"
   print generateEuropeanCallPrices(S[-1], strikePrice,  float(days), N, volatility, r, 0, n)
   print "Calculating put price. If n or N is large this could take a while...\nPut price is:",
   print generateEuropeanPutPrices(S[-1], strikePrice, float(days), N, volatility, r, 0, n)


if __name__ == "__main__":
   main(sys.argv[1:])

# discount=math.exp(-1*0.01*1.0)

# print generateEuropeanPutPrices(398.79, 300.0, 2.5, 1, 0.32, 0.01, 0, 100000)	# 	random = denormal[t_j]
