import pySAS.PyTriosFork.ramses_calibrate as rc
import pySAS.PyTriosFork.calibrate_tilt as ct
import numpy as np
import argparse
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def calibrateData(filePath):

    calData = rc.importCalFiles('./CalFolder')

    calibratedData = []

    with open(filePath, "r") as file:
    
        for line in file:

            sample = line.split('\t')

            serialln = sample[0]
            msdate = sample[1]
            integrationTime = sample[2]
            
            if(serialln == '514C'):
                tiltBytes = sample[3].split(' ')
                specData = sample[4].split(',')

                specData = [int(i) for i in specData]

                calibratedSpec = rc.raw2cal_Air(specData,msdate,serialln,calData, wlOut=np.arange(320, 955, 3.3))

                inclination = ct.getIncValue(tiltBytes)

                calibratedSpec = calibratedSpec[1:193]

                calibratedAll = [serialln, msdate, integrationTime,inclination, calibratedSpec]

                calibratedData.append(calibratedAll)
            else:
                specData = sample[4].split(',')

                specData = [int(i) for i in specData]

                calibratedSpec = rc.raw2cal_Air(specData,msdate,serialln,calData, wlOut=np.arange(320, 955, 3.3))

                calibratedSpec = calibratedSpec[1:193]

                calibratedAll = [serialln, msdate, integrationTime, calibratedSpec]

                calibratedData.append(calibratedAll)
        
    return calibratedData, serialln

def calibrateDataFromPySAS(deque):

    calData = rc.importCalFiles('./pySAS/PyTriosFork/CalFolder')

    calibratedData = {}

    for line in deque:

        sample = line.split('\t')

        serialln = sample[0]
        msdate = sample[1]
        integrationTime = sample[2]
        if(serialln == '514C'):
            tiltBytes = sample[3].split(' ')
            specData = sample[4].split(',')

            specData = [int(i) for i in specData]

            calibratedSpec = rc.raw2cal_Air(specData,msdate,serialln,calData, wlOut=np.arange(320, 955, 3.3))

            pitch,roll = ct.getIncValue(tiltBytes)

            calibratedSpec = calibratedSpec[1:193]

            calibratedAll = [serialln, msdate, integrationTime, calibratedSpec, pitch, roll]

            calibratedData[serialln] = calibratedAll
        else:
            specData = sample[4].split(',')

            specData = [int(i) for i in specData]

            calibratedSpec = rc.raw2cal_Air(specData,msdate,serialln,calData, wlOut=np.arange(320, 955, 3.3))

            calibratedSpec = calibratedSpec[1:193]

            calibratedAll = [serialln, msdate, integrationTime, calibratedSpec]

            calibratedData[serialln] = calibratedAll

    return calibratedData

def saveCalibratedDataTxt(serialln, calibratedData, filePath):
    with open('./tmp/'+filePath, "w") as f:
        if(serialln == '514C'):
            for calibratedSample in calibratedData:

                serialln, msdate, integrationTime, inclination = calibratedSample[0], calibratedSample[1], calibratedSample[2], calibratedSample[3]
                f.write(f'{serialln} {msdate} {integrationTime} {inclination} ')
                calibratedSpec = calibratedSample[4]

                for value in calibratedSpec:
                    f.write(f'{value} ')

                f.write('\n')  
        else:
            for calibratedSample in calibratedData:

                serialln, msdate, integrationTime = calibratedSample[0], calibratedSample[1], calibratedSample[2]
                f.write(f'{serialln} {msdate} {integrationTime} ')
                calibratedSpec = calibratedSample[3]

                for value in calibratedSpec:
                    f.write(f'{value} ')

                f.write('\n') 

def saveCalibratedDataCsv(calibratedData, filePath):

    wlColumns = np.arange(320,951,3.3)
    stringColumns = ['serialPort', 'msDate', 'integrationTime']

    allColumnsNames = stringColumns + wlColumns.tolist()
    
    calibratedArrayCsv = [sample[:-1] + sample[-1].tolist() for sample in calibratedData]
    
    calibratedArrayCsv.insert(0,allColumnsNames)

    with open('./tmp/'+ filePath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(calibratedArrayCsv)
    return 

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', type=str, required=True, help='Path for the input file')
    parser.add_argument('-o', '--outputFile', type=str, required=True, help='Path for the output file')
    args = parser.parse_args()
    return args

def plotCalibration(filePath):
    calibrationDf = pd.read_csv('./tmp/'+filePath)

    rows = 4
    columns = 5

    fig,axs = plt.subplots(rows,columns, sharex=True, sharey=True)
    serialPort = calibrationDf.iloc[0,0]
    integrationTime = calibrationDf.iloc[0,2]
    waveLengths = calibrationDf.columns[3:]
    waveLengths = [float(x) for x in waveLengths]
    xTicksVector = np.arange(320, 950, 100) 

    for i,ax in enumerate(axs.flat):
        # print(waveLengths)
        irradianceValues = calibrationDf.iloc[i,3:]
        msDate = calibrationDf.iloc[i,1]
        # print(irradianceValues)

        ax.plot(waveLengths,irradianceValues)
        ax.set(xlabel='Wavelenght(nm)', ylabel='Irradiance(W/m²)', title=f'{msDate}', xticks=xTicksVector)
        ax.label_outer()
        
    fig.suptitle(f'Serial Port: {serialPort}, Integration Time: {integrationTime}')
    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    plt.show()
    return

def animateCalibration(filePath):

    calibrationDf = pd.read_csv('./tmp/'+filePath)

    numRows = len(calibrationDf)
    fig,axs = plt.subplots()
    waveLengths = calibrationDf.columns[3:]
    waveLengths = [float(x) for x in waveLengths]
    irradianceValues = calibrationDf.iloc[0,3:]
    linePlot = axs.plot(waveLengths,irradianceValues)[0]
    yTicksVector = np.arange(0, 0.301, 0.05)
    xTicksVector = np.arange(320, 950, 100)

    axs.set(xlabel='Wavelenght(nm)', ylabel='Irradiance(W/m²)', xticks=xTicksVector, yticks=yTicksVector)
    # plt.show()

    def update(frame):
        curMsDate = calibrationDf.iloc[frame,1] 
        # axs.set_label(curMsDate)
        irradianceValues = calibrationDf.iloc[frame, 3:]
        linePlot.set_ydata(irradianceValues)
        return linePlot
    
    ani = animation.FuncAnimation(fig=fig, func=update, frames=numRows, interval=1000)
    # plt.show()
    ani.save(filename="./tmp/pillow_example.mp4", writer="ffmpeg")

    return

if __name__ == '__main__':
   
    import debugpy
    debugpy.listen(("localhost", 5600)) 
    print("⏳ Waiting for debugger attach...")
    debugpy.wait_for_client() 

    args = parseArgs()

    calibratedData = calibrateData(args.inputFile)
    saveCalibratedDataTxt(calibratedData, args.outputFile + '.txt')
    saveCalibratedDataCsv(calibratedData, args.outputFile + '.csv')

    plotCalibration(args.outputFile + '.csv')
    # animateCalibration(args.outputFile + '.csv')