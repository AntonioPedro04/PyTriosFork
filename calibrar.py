import ramses_calibrate as rc
import numpy as np
import argparse

#import debugpy
#debugpy.listen(("localhost", 5678)) 
#print("⏳ Waiting for debugger attach...")
#debugpy.wait_for_client() 

def calibrateData(filePath):

    calData = rc.importCalFiles('./CalFolder')

    calibratedData = []

    with open(filePath, "r") as file:
    
        for line in file:

            sample = line.split('\t')

            serialln = sample[0]
            msdate = sample[1]
            integrationTime = sample[2]
            specData = sample[3].split(',')

            specData = [int(i) for i in specData]

            calibratedSpec = rc.raw2cal_Air(specData,msdate,serialln,calData, wlOut=np.arange(320, 955, 3.3))

            print(len(calibratedSpec))

            calibratedAll = [serialln, msdate, integrationTime, calibratedSpec]

            calibratedData.append(calibratedAll)
    
    return calibratedData

def saveCalibratedData(calibratedData, filePath):
    with open(filePath, "w") as f:

        for calibratedSample in calibratedData:

            serialln, msdate, integrationTime = calibratedSample[0], calibratedSample[1], calibratedSample[2]
            f.write(f'{serialln} {msdate} {integrationTime} ')
            calibratedSpec = calibratedSample[3]

            for value in calibratedSpec:
                f.write(f'{value} ')

            f.write('\n')  

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', type=str, required=True, help='Path for the input file')
    parser.add_argument('-o', '--outputFile', type=str, required=True, help='Path for the output file')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
   
   args = parseArgs()

   calibratedData = calibrateData(args.inputFile)
   saveCalibratedData(calibratedData, args.outputFile)

