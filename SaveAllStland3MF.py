#Author- Elizabeth Greene
#Description- export bodies to individual STLs
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

        # open folder dialog to select the output folder
        folderDialog = ui.createFolderDialog()
        folderDialog.title = 'Select output folder'
        folderDialog.filter = ''

        dialogResult = folderDialog.showDialog()

        if dialogResult != adsk.core.DialogResults.DialogOK:
            ui.messageBox('Export cancelled')
            return
        
        outputDirectory = folderDialog.folder

        # get the root component of the active design
        components = design.allComponents

        for component in components:
                ui.statusMessage = 'Component: ' + component.name
                adsk.doEvents
                
                # get all bodies in the root component
                bodies = component.bRepBodies

                # create the export manager
                exportMgr = adsk.fusion.ExportManager.cast(design.exportManager)

                for body in bodies:
                    if body.isSolid:
                        #Update Status Bar text
                        ui.statusMessage = 'Exporting: ' + component.name + ' ' + body.name
                        adsk.doEvents

                        # Export Stl file
                        fileName = os.path.join(outputDirectory, '{}.stl'.format(body.name))

                        # create the STL export options
                        stlExportOptions = exportMgr.createSTLExportOptions(body)

                        # set refinement of STL
                        stlExportOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium

                        # the filename to be export too
                        stlExportOptions.filename = fileName

                        exportMgr.execute(stlExportOptions)

                        # Export 3mf file
                        fileName = os.path.join(outputDirectory, '{}.3mf'.format(body.name))

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