#!/usr/bin/python

# This is a tool to transfer from cityscapes lable file *.json to Ygomi class definitions
# The transfer rule is https://confluence.ygomi.com:8443/display/RRT/Classification+Definition+for+Semantic+Segmentation#ClassificationDefinitionforSemanticSegmentation-FromCityscapestoYgomi
# Parameters:
#    - inputJsonDir: abs dir of the input JSON label files, with cityscapes label format
#    - outputJsonDir: abs dir of the output JSON label files, with Ygomi lable format
#

import os, sys, getopt

sys.path.append( os.path.normpath( os.path.join( os.path.dirname( __file__ ) , '..') ) )
from helper.annotation import Annotation

labelTransferDict = {
        # cityscape:            ygo
        'unlabeled':            'unlabelled',
        'ego vehicle':          'static',
        'rectification border': 'unlabelled',
        'out of roi':           'unlabelled',
        'static':               'static',
        'dynamic':              'unlabelled',
        'ground':               'static',
        'road':                 'road',
        'sidewalk':             'sidewalk',
        'parking':              'road',
        'rail track':           'static',
        'building':             'building',
        'wall':                 'wall',
        'fence':                'fence',
        'guard rail':           'fence',
        'bridge':               'bridge',
        'tunnel':               'tunnel',
        'pole':                 'pole',
        'polegroup':            'fence',
        'traffic light':        'traffic light',
        'traffic sign':         'traffic sign',
        'vegetation':           'vegetation',
        'terrain':              'terrain',
        'sky':                  'sky',
        'person':               'person',
        'rider':                'rider',
        'car':                  'car',
        'truck':                'truck',
        'bus':                  'truck',
        'caravan':              'truck',
        'trailer':              'car',
        'train':                'unlabelled',
        'motorcycle':           'rider',
        'bicycle':              'rider',
        'ego vehicle':          'ego vehicle',
        'license plate':        '',
}

def annotationConvert(annotationIn):
    annotationOut = Annotation()
    annotationOut.imgWidth = annotationIn.imgWidth
    annotationOut.imgHeight = annotationIn.imgHeight

    # for each label in the json file
    for obj in annotationIn.objects:
        label = obj.label

        # If the label is not known, but ends with a 'group' (e.g. cargroup)
        # try to remove the group and see if that works
        if (not label in labelTransferDict) and label.endswith('group'):
            label = label[:-len('group')]

        if not label in labelTransferDict:
            print "Label '{}' not known.".format(label)
            continue

        newLabel = labelTransferDict[label]

        if newLabel != obj.label:
            print "    '{}' -> '{}'".format(obj.label, newLabel)

        obj.label = newLabel
        if obj.label != '':
            annotationOut.objects.append(obj)

    return annotationOut

# Print an error message and quit
def printError(message):
    print('ERROR: {}'.format(message))
    print('')
    print('USAGE:')
    printHelp()
    sys.exit(-1)

def printHelp():
    print('{} [OPTIONS] inputJsonDir outputJsonDir'.format(os.path.basename(sys.argv[0])))

def cs2yg(argv):
    try:
        opts, args = getopt.getopt(argv,"ht")
    except getopt.GetoptError:
        printError( 'Invalid arguments' )

    inputJsonDir  = args[0]
    outputJsonDir = args[1]

    if os.path.isfile(inputJsonDir):
        if '_polygons.json' in inputJsonDir:
            outJson = inputJsonDir.replace("_polygons.json", ".json")
        elif '.psp.json' in inputJsonDir:
            outJson = inputJsonDir.replace(".psp.json", ".json")
        else:
            return

        # print ">>>>" + inputJsonDir
        annotationIn = Annotation()
        annotationIn.fromJsonFile(inputJsonDir)

        annotationOut = annotationConvert(annotationIn)
        annotationOut.toJsonFile(outJson)
        print("saved to json: " + outJson)

    else:
        # search for JSON configuration files
        for dirpath, dirnames, filenames in os.walk(inputJsonDir):
            for filename in filenames:
                if '_polygons.json' not in filename and '.psp.json' not in filename:
                    continue

                inJson = os.path.join(dirpath, filename)

                print ">>>>" + inJson

                annotationIn = Annotation()
                annotationIn.fromJsonFile(inJson)

                # put the output file under specified directory, and use the same name as input file
                outJson = outputJsonDir + '/' + inJson[len(inputJsonDir):]
                #outJson = outJson.replace(".json", "_ygo.json")

                outJsonDir = os.path.dirname(os.path.abspath(outJson))
                if not os.path.exists(outJsonDir):
                    os.makedirs(outJsonDir)

                annotationOut = annotationConvert(annotationIn)

                annotationOut.toJsonFile(outJson)

# call the main method
if __name__ == "__main__":
    cs2yg(sys.argv[1:])
