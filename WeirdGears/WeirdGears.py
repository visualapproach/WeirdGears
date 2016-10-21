#Author-Thomas Landahl
#Description- make non circular planet gears for fun


import adsk.core, adsk.fusion, traceback, math


# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_sunPeaks = adsk.core.ValueCommandInput.cast(None)
_sunTeeth = adsk.core.ValueCommandInput.cast(None)
_pitch = adsk.core.ValueCommandInput.cast(None)
_planetPeaks = adsk.core.ValueCommandInput.cast(None)
_amplitude = adsk.core.ValueCommandInput.cast(None)
_backlash = adsk.core.ValueCommandInput.cast(None)

_handlers = []

commandId = 'weirdGears3AddIn'
commandName = 'WeirdGears3'
commandDescription = 'Making sinusoidal planet gears.'

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create a command definition and add a button to the CREATE panel.
        cmdDef = _ui.commandDefinitions.addButtonDefinition(commandId, commandName, commandDescription, 'resources/SpurGear')
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.addCommand(cmdDef)

        # Connect to the command created event.
        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "WeirdGears" command has been added\nto the CREATE panel of the MODEL workspace.')

    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.itemById(commandId)
        if gearButton:
            gearButton.deleteMe()

        cmdDef = _ui.commandDefinitions.itemById(commandId)
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Verfies that a value command input has a valid expression and returns the
# value if it does.  Otherwise it returns False.  This works around a
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager

        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandCreated event.
class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            #_ui.messageBox('createdevent start') #DEBUG

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _sunPeaks, _sunTeeth, _pitch, _planetPeaks, _amplitude, _backlash

            # Create value input
            inputs.addTextBoxCommandInput('info', 'Info', 'Total # of peaks must be even number', 2, True)
            _sunPeaks = inputs.addValueInput('sunPeaks', 'Sun gear peaks', '', adsk.core.ValueInput.createByReal(3.0))
            _sunTeeth = inputs.addValueInput('sunTeeth', 'Sun gear # of teeth (MUST be divisible by sun gear peaks)', '', adsk.core.ValueInput.createByReal(24.0))
            _pitch = inputs.addValueInput('pitch', 'tooth pitch (Arc dist along pitch dia)', 'cm', adsk.core.ValueInput.createByReal(1.0))
            _planetPeaks = inputs.addValueInput('planetPeaks', 'Outer gear peaks (must be > sun peaks)', '', adsk.core.ValueInput.createByReal(5.0))
            _amplitude = inputs.addValueInput('amplitude', 'Amplitude in percent (5-15 should do)', '', adsk.core.ValueInput.createByReal(7.0))
            _backlash = inputs.addValueInput('backlash', 'Backlash (in cm)', '', adsk.core.ValueInput.createByReal(0.1))

            # Connect to the command related events.
            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            onInputChanged = GearCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            onValidateInputs = GearCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            des = adsk.fusion.Design.cast(_app.activeProduct)

            # Get the values from the command inputs.
            sunPeaks = _sunPeaks.value
            sunTeeth = _sunTeeth.value
            pitch = _pitch.value
            planetPeaks = _planetPeaks.value
            amplitude = _amplitude.value
            backlash = _backlash.value

            drawGears(des, int(sunPeaks), int(sunTeeth), pitch, int(planetPeaks), amplitude, backlash)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class GearCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            a = 0 #debug
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the validateInputs event.
class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            #_ui.messageBox('No code here yet... (validateInputsHandler)')

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Builds the weird gears
def drawGears(design, sunPeaks, sunTeeth, pitch, planetPeaks, amplitude, backlash):
    try:
        # Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)
        newComp = adsk.fusion.Component.cast(newOcc.component)

        # Create new sketches.
        sketches = newComp.sketches
        xyPlane = newComp.xYConstructionPlane
        sunSketch = sketches.add(xyPlane)
        planetSketch = sketches.add(xyPlane)
        carriageSketch = sketches.add(xyPlane)
        sunSketch.name = 'sun gear sketch'
        planetSketch.name = 'planet gear sketch'
        carriageSketch.name = 'carriage gear sketch'
        sunSketch.isComputeDeferred = True
        planetSketch.isComputeDeferred = True
        carriageSketch.isComputeDeferred = True

        # Create an object collection for the points.
        sunPoints = adsk.core.ObjectCollection.create()
        planetPoints = adsk.core.ObjectCollection.create()
        carriagePoints = adsk.core.ObjectCollection.create()

        gearRatio = (planetPeaks+sunPeaks)/sunPeaks #don't ask me why, it's just the way it is
        sunCircumference = sunTeeth * pitch
        planetCircumference = round(gearRatio * sunCircumference - sunCircumference, 5)
        planetTeeth = int(round(planetCircumference / pitch))
        sunRadius = sunCircumference/(2*math.pi) #this is only true for a circle, but a good start.
        module = (2*sunRadius)/sunTeeth
        dedendum = 1.5*module


        #it will be adjusted below
        amp = sunRadius*amplitude/100 #how tall the peaks is

        planetRadius = sunRadius*gearRatio-sunRadius
        PA = 20*math.pi/180 #Pressure Angle in radians


        #try to measure the circumference by integrating
        d = 0
        customRadius = amp * math.sin(0)+sunRadius #customradius = sun radius + sine function (depending on the sampled angle)
        prev_x = math.sin(0)*customRadius
        prev_y = math.cos(0)*customRadius

        ratio = 2 #just to get the loop going
        newradius = sunRadius #newradius = adjusted mean sun radius

        while(ratio>1.00001 or ratio<0.99999):
            d = 0
            for a in range(1, 720+1, 1):
                angle = a*math.pi/360
                customRadius = amp * math.sin(angle*sunPeaks)+newradius
                x = math.sin(angle)*customRadius
                y = math.cos(angle)*customRadius
                dx = x-prev_x
                dy = y-prev_y
                d += math.sqrt(dx**2+dy**2)
                prev_x = x
                prev_y = y
            ratio = d/sunCircumference
            newradius = newradius/ratio
        sunRadius = newradius

        #Now draw the points with the adjusted radius
        d = pitch/2+backlash
        prev_x = 0
        prev_y = 0
        resolution = 20
        for a in range(0,sunTeeth*resolution,1):
            angle = a*2*math.pi/(sunTeeth*resolution)
            customRadius = amp * math.sin(angle*sunPeaks)+sunRadius
            x = math.sin(angle)*customRadius
            y = math.cos(angle)*customRadius
            dx = x-prev_x
            dy = y-prev_y
            prev_x = x
            prev_y = y
            if a > 0:
                d += math.sqrt(dx**2+dy**2)
            if ((pitch/2+backlash) - d) < (pitch/resolution):
                d = d-(pitch/2+backlash)
                backlash = -backlash
                sunPoints.add(adsk.core.Point3D.create(x, y, 0))

        # Create the spline.
        spline = sunSketch.sketchCurves.sketchFittedSplines.add(sunPoints)
        spline.isClosed = True
        spline.isConstruction = True

        pbh = sunRadius - sunRadius * math.cos(PA) #pressure angle

        makeTeeth(sunSketch, sunPoints, dedendum, True, module, pbh, sunRadius)
        axleRadius = sunRadius/5
        sunSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), axleRadius)
        sunSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, sunRadius/2, 0), axleRadius/2)



        #***********planet (probably the wrong term but I can't be bothered to change)********************
        #try to measure the circumference by integrating
        d = 0
        customRadius = amp * math.sin(0)+planetRadius #customradius = sun radius + sine function (depending on the sampled angle)
        prev_x = math.sin(0)*customRadius
        prev_y = math.cos(0)*customRadius

        ratio = 2 #just to get the loop going
        newradius = planetRadius #newradius = adjusted mean planet radius
        resolution = 40

        while(ratio>1.000001 or ratio<0.999999):
            d = 0
            for a in range(1, planetTeeth*resolution+1, 1):
                angle = a*2*math.pi/(planetTeeth*resolution)
                customRadius = amp * math.sin(angle*sunPeaks-angle*sunPeaks*gearRatio)+newradius
                x = math.sin(angle)*customRadius
                y = math.cos(angle)*customRadius
                dx = x-prev_x
                dy = y-prev_y
                d += math.sqrt(dx**2+dy**2)
                prev_x = x
                prev_y = y
            ratio = d/planetCircumference
            newradius = newradius/ratio
        planetRadius = newradius

        #Now draw the points with the adjusted radius
        backlash = -abs(backlash)
        d = pitch/2+backlash
        prev_x = 0
        prev_y = 0
        for a in range(0,planetTeeth*resolution,1):
            angle = a*2*math.pi/(planetTeeth*resolution)
            customRadius = amp * math.sin(angle*sunPeaks-angle*sunPeaks*gearRatio)+planetRadius
            x = math.sin(angle)*customRadius
            y = math.cos(angle)*customRadius
            dx = x-prev_x
            dy = y-prev_y
            prev_x = x
            prev_y = y
            if a > 0:
                d += math.sqrt(dx**2+dy**2)
            if ((pitch/2+backlash) - d) < (pitch/resolution):
                d = d-(pitch/2+backlash)
                backlash = -backlash
                planetPoints.add(adsk.core.Point3D.create(x, y, 0))

        # Create the spline.
        spline = planetSketch.sketchCurves.sketchFittedSplines.add(planetPoints)
        spline.isClosed = True
        spline.isConstruction = True
        ofC = adsk.core.ObjectCollection.create()
        ofC.add(spline)
        offsetSplines = planetSketch.offset(ofC, adsk.core.Point3D.create(0, 2*planetRadius, 0), planetRadius/5)
        offsetSplines[0].isConstruction = False

        #pbh = planetRadius - planetRadius *math.cos(PA) #pressure angle
        makeTeeth(planetSketch, planetPoints, dedendum, False, module, pbh, sunRadius)
        planetSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), axleRadius-0.08)


#*******carriage (yeah yeah it's probably the planet)*************

        #customRadius = (planetRadius-sunRadius)/2
        customRadius = ((planetCircumference/math.pi/2)-(sunCircumference/math.pi/2))/2 #testing to big gear with matching pitch

        #Now draw the points with the adjusted radius
        backlash = abs(backlash)
        numTeeth = int((planetTeeth-sunTeeth)/2)
        d = 2*math.pi*customRadius/(2*numTeeth)
        for a in range(numTeeth*2):
            v = float((a*d+backlash)/customRadius)
            x = math.sin(v)*customRadius
            y = math.cos(v)*customRadius
            carriagePoints.add(adsk.core.Point3D.create(x, y, 0))
            backlash = -backlash

        # Create the spline.
        spline = planetSketch.sketchCurves.sketchFittedSplines.add(planetPoints)
        spline.isClosed = True
        spline.isConstruction = True

        makeTeeth(carriageSketch, carriagePoints, dedendum, True, module, pbh, customRadius)
        carriageSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), customRadius/3)

        carriageSketch.isComputeDeferred = False
        sunSketch.isComputeDeferred = False
        planetSketch.isComputeDeferred = False

        newComp.name = '#teeth:'+str(planetTeeth)+'-'+str(sunTeeth)+'-'+str(numTeeth)
        return newComp

    except Exception as error:
        _ui.messageBox("drawGear Failed : " + str(error))
        return None

def getAngle(p, origo):
    x = p.x - origo.geometry.x
    y = p.y - origo.geometry.y
    if y>0:
        if x>0:
            return math.atan(x/y)
        else:
            return 2*math.pi+math.atan(x/y)
    elif y == 0:
            if x > 0:
                return math.pi
            else:
                return math.pi*1.5
    elif x > 0:
        return math.pi + math.atan(x/y)
    else:
        return math.pi + math.atan(x/y)


def makeTeeth(currentSketch, pointsList, dedendum, external, m, pitchBaseHeight, r):
    try:
        flankPoints = adsk.core.ObjectCollection.create()
        outerPoints = adsk.core.ObjectCollection.create()
        innerPoints = adsk.core.ObjectCollection.create()
        #make a general circle to represent the general curvature. Build involute tooth upon this circle
        #Every other point on the curve is a right handed flank. loop through them by starting at #0.
        for p in range(0,pointsList.count,1):
            if external:
                a = getAngle2(pointsList[p-2], pointsList[(p+2)%pointsList.count])+math.pi/2
            else:
                a = getAngle2(pointsList[p-2], pointsList[(p+2)%pointsList.count])-math.pi/2
            origo = adsk.core.Point3D.create(0, 0, 0)
            origo.x = pointsList[p].x+math.sin(a)*r
            origo.y = pointsList[p].y+math.cos(a)*r
            c = currentSketch.sketchCurves.sketchCircles.addByCenterRadius(origo, r)
            c.isConstruction = True

            bcr = c.radius - pitchBaseHeight # bcr = base circle radius
            arc = math.sqrt((c.radius)**2 - (bcr)**2)
            theta = (arc/bcr)-math.atan(arc/bcr) # theta is the angle difference from root to point on flank
            alpha = getAngle2(origo, pointsList[p]) #alpha is the angle from origo to the pitchdia point

            #first , if external gear or internal with negative curvature,
            #add dedendum point (at the root circle (should be inside bcr))
            #(meaning- skip dedendum if it intrudes on the open space between gears)
            if p % 2 == 0:
                beta = -theta+alpha
            else:
                beta = theta+alpha #beta is the absolute angle from origo
            x = origo.x + math.sin(beta)*(c.radius - dedendum)
            y = origo.y + math.cos(beta)*(c.radius - dedendum)

            negCurvature = False
            if (x**2+y**2) > (pointsList[p].x**2+pointsList[p].y**2):
                negCurvature = True
            # Plist is to get the angular position at some height intervals along the flank
            if external and (not negCurvature):
                plist = [pitchBaseHeight/2, pitchBaseHeight, pitchBaseHeight+m/2, pitchBaseHeight+m*0.8]
            elif (not external) and (not negCurvature):
                plist = [pitchBaseHeight/2, pitchBaseHeight, pitchBaseHeight+dedendum/2, pitchBaseHeight+dedendum]
            elif external and negCurvature:
                plist = [pitchBaseHeight/2, pitchBaseHeight, pitchBaseHeight+dedendum/2, pitchBaseHeight+dedendum]
            else:
                plist = [pitchBaseHeight/2, pitchBaseHeight, 1.5*pitchBaseHeight, 2*pitchBaseHeight]

            if (external and (not negCurvature)) or (negCurvature and (not external)):
                flankPoints.add(adsk.core.Point3D.create(x, y, 0))

            #then add base circle point
            x = origo.x + math.sin(beta)*(bcr)
            y = origo.y + math.cos(beta)*(bcr)
            flankPoints.add(adsk.core.Point3D.create(x, y, 0))

            #add 3 more points up to before tooth tip
            for n in range(len(plist)):
                arc = math.sqrt(abs((bcr+plist[n])**2 - bcr**2))
                #beta = absolute angle from origo to the flank point at specified height (h*tmp).
                #  this is the same as alpha when measured at the pitchradius
                #theta = relative angle between pitchdiameter/flank crossing point and the root of the flank (where h=0)
                if p % 2 == 0:
                    beta = (arc/bcr)-math.atan(arc/bcr)-theta+alpha
                else:
                    beta = -((arc/bcr)-math.atan(arc/bcr))+theta+alpha #beta is the absolute angle from origo
                x = origo.x + math.sin(beta)*(bcr+plist[n])
                y = origo.y + math.cos(beta)*(bcr+plist[n])
                flankPoints.add(adsk.core.Point3D.create(x, y, 0))

            flankPoints.add(adsk.core.Point3D.create(x, y, 0))

            spline = currentSketch.sketchCurves.sketchFittedSplines.add(flankPoints)
            if flankPoints[-1].x**2 + flankPoints[-1].y**2 > flankPoints[0].x**2 + flankPoints[0].y**2:
                #last point is outer
                outerPoints.add(flankPoints[-1])
                innerPoints.add(flankPoints[0])
            else: #last point is inner
                innerPoints.add(flankPoints[-1])
                outerPoints.add(flankPoints[0])
            flankPoints.clear()
            #delete the temporary  circle from the sketch
            c.deleteMe()

        for p in range(0,int(innerPoints.count),2):
            currentSketch.sketchCurves.sketchLines.addByTwoPoints(innerPoints[p-1], innerPoints[p])
            currentSketch.sketchCurves.sketchLines.addByTwoPoints(outerPoints[p], outerPoints[p+1])
        innerPoints.clear()
        outerPoints.clear()
    except Exception as error:
        _ui.messageBox("makeTeeth Failed : " + str(error))
        return None

def getAngle2(p1, p2):
    x = p2.x - p1.x
    y = p2.y - p1.y
    if y>0:
        if x>0:
            return math.atan(x/y)
        else:
            return 2*math.pi+math.atan(x/y)
    elif y == 0:
            if x > 0:
                return math.pi
            else:
                return math.pi*1.5
    elif x > 0:
        return math.pi + math.atan(x/y)
    else:
        return math.pi + math.atan(x/y)
