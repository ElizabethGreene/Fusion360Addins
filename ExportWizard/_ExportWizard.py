#Author- Elizabeth Greene
#Description- One-click Export of Fusion F3d file, STL, and 3mf files for all bodies in the active design
#Inspired by Sample Script https://www.reddit.com/r/Fusion360/comments/166ub6r/for_loop_for_exporting_bodies/ by CharlieX

# import the required libraries
import adsk.core, adsk.fusion, os, traceback

def run(context):
    ui = None
    try:
        # get the User Interface object
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # get the active design
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('run from within a design with bodies', 'No Design')
            return

        # open file dialog to select the output file

        msg = ''
        # Set styles of file dialog.
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False 
        fileDlg.filter = 'Fusion 360 files (*.F3D)'
        fileDlg.filterIndex = 0
        
        # Show file save dialog
        fileDlg.title = 'Save all Files Dialog'
        dlgResult = fileDlg.showSave()
        if dlgResult == adsk.core.DialogResults.DialogOK:
            msg += '\nFile to Save: {}'.format(fileDlg.filename)
        else:
            return

        if dlgResult != adsk.core.DialogResults.DialogOK:
            ui.messageBox('Export cancelled')
            return
        
        # Get the output directory from the selected file
        outputDirectory = os.path.dirname(fileDlg.filename)
        
        # Export the Fusion F3d file to fileDlg.filename
        exportMgr = adsk.fusion.ExportManager.cast(design.exportManager)
        f3dExportOptions = exportMgr.createFusionArchiveExportOptions(fileDlg.filename)
        exportMgr.execute(f3dExportOptions)

        # Export the .Step file to the same directory
        stepFileName = os.path.join(outputDirectory, os.path.splitext(os.path.basename(fileDlg.filename))[0] + '.step')
        stepExportOptions = exportMgr.createSTEPExportOptions(stepFileName)
        exportMgr.execute(stepExportOptions)    

        # Now iterate through the components and export each body as an STL and 3Mf file        

        # get the root component of the active design
        components = design.allComponents

        # Create a hash table to store the body names so we can increment the file name if there are duplicates
        bodyNames = {}

        for component in components:
                ui.statusMessage = 'Component: ' + component.name
                adsk.doEvents
                
                # get all bodies in the root component
                bodies = component.bRepBodies

                # reusing the previously created export manager
                
                for body in bodies:
                    if body.isSolid:
                        #Update Status Bar text
                        ui.statusMessage = 'Exporting: ' + component.name + ' ' + body.name
                        adsk.doEvents

                        outputfilename = body.name

                        # Remove special characters from the bodyname
                        outputfilename = RemoveSpecialCharactersFromFilename(outputfilename)

                        # Make the filename unique, i.e. in case a project has multiple bodies named Body1
                        outputfilename = MakeFilenameUnique(outputfilename, bodyNames)
         
                        # Export Stl file
                        fileName = os.path.join(outputDirectory, '{}.stl'.format(outputfilename))

                        # create the STL export options
                        stlExportOptions = exportMgr.createSTLExportOptions(body)

                        # set refinement of STL
                        stlExportOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium

                        # the filename to be export too
                        stlExportOptions.filename = fileName

                        exportMgr.execute(stlExportOptions)

                        # Export 3mf file
                        fileName = os.path.join(outputDirectory, '{}.3mf'.format(outputfilename))

                        # create the 3mf export options
                        c3mfExportOptions = exportMgr.createC3MFExportOptions(body)

                        # set refinement of 3mf
                        c3mfExportOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium

                        # the filename to be export too
                        c3mfExportOptions.filename = fileName

                        exportMgr.execute(c3mfExportOptions)

        #Clear Status Bar text
        ui.statusMessage = ''
        adsk.doEvents

        ui.messageBox('Export Completed')


    except:
        if ui:
            ui.messageBox('failed:\n{}'.format(traceback.format_exc()))


# MakeFilenameUnique function
# This function takes a body name and a hash table of all the filenames that have been used.
# It returns a unique filename by appending a number to the end of the filename if it is already in the hash table.
def MakeFilenameUnique(bodyName, bodyNames):
    # Check if the body name is already in the hash table
    if bodyName in bodyNames:
        # If it is, increment the count
        bodyNames[bodyName] += 1

    else:
        # If it is not, add it to the hash table
        bodyNames[bodyName] = 0

    # If the count is greater than 0, append the count to the filename
    if bodyNames[bodyName] > 0:
        newbodyname = bodyName + '(' + str(bodyNames[bodyName]) + ')'
        # and pass the bodyname back to the this function again to check if the new name is unique
        return MakeFilenameUnique(newbodyname, bodyNames)

    return bodyName


# RemoveSpecialCharactersFromFilename function
# This function takes a filename and removes any special characters that are not allowed in filenames.
# e.g. / \ : * ? " < > |
# It also removes leading spaces and trailing spaces.
# and if a filename is blank or invalid, it returns "BadBodyName"
def RemoveSpecialCharactersFromFilename(filename):
    # Remove leading and trailing spaces
    newfilename = filename.strip()

    # List of special characters that are not allowed in filenames
    specialCharacters = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    # If filename contains specialCharacters, remove them.
    for character in specialCharacters:
        newfilename = newfilename.replace(character, '')

    # If the filename is blank or invalid, return "BadBodyName"
    if newfilename == '':
        return 'BadBodyName'

    # Otherwise, return the new filename
    return newfilename
    
