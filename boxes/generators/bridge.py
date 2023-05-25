#!/usr/bin/env python3
# Copyright (C) 2013-2022 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *

class Bridge(Boxes):
    """Simple Girder Bridge and Suport stucture. """

    ui_group = "Misc"

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings, finger=10.0,space=10.0)
        self.buildArgParser(x=70, h=150)
        self.argparser.add_argument(
            "--bridgeGirderSpan",  action="store", type=float, default=300,
            help="Length of the Bridge Girder Span in mm. Ignored if bridgeAngle and centerlineRadius are set. LGB10000=300 LGB10600=600 LGB10610=1200")
        self.argparser.add_argument(
            "--bridgeGirderHeight",  action="store", type=float, default=45,
            help="Height of the Bridge Girder in mm")
        self.argparser.add_argument(
            "--bridgeGirderWidth",  action="store", type=float, default=90,
            help="Width of the Bridge Girder in mm")
        self.argparser.add_argument(
            "--bridgeDeckWidth",  action="store", type=float, default=120,
            help="Width of the Bridge Deck in mm")
        self.argparser.add_argument(
            "--centerlineRadius",  action="store", type=float, default=0,
            help="Centerline radius of curve of the bridge. Defaults to straight/0. LGB R1=600 R2=765 R3=1175")
        self.argparser.add_argument(
            "--bridgeAngle",  action="store", type=float, default=0,
            help="Degree Angle of the curve covered by the bridge. Not needed if radius is 0. LGB R1=30 R2=30 R3=22.5")
        self.argparser.add_argument(
            "--edgeOffset",  action="store", type=float, default=10,
            help="Offset of girders from edge of square")
        self.argparser.add_argument(
            "--webThickness",  action="store", type=float, default=10,
            help="thickness of webbing")
        self.argparser.add_argument(
            "--numBulkheads",  action="store", type=float, default=2,
            help="number of Bulkheads")
        self.argparser.add_argument(
            "--matingHolesDiam",  action="store", type=float, default=5,
            help="diameter of the holes in the bottom of the bridge span plate and top of the support to join them via a pin in mm")

    def ringSegmentWithEdges(self, r_outside, r_inside, angle, n=1, move=None):
        """Ring Segment

        :param r_outside: outer radius
        :param r_inside: inner radius
        :param angle: angle the segment is spanning
        :param n: (Default value = 1) number of segments
        :param move: (Default value = "")
        """
        space = 360 * self.spacing / r_inside / 2 / math.pi
        nc = int(min(n, 360 / (angle+space)))

        while n > 0:
            if self.move(2*r_outside, 2*r_outside, move, True):
                return
            self.moveTo(0, r_outside, -90)
            for i in range(nc):
                self.polyline(
                    0, (angle, r_outside), 0, 90, (r_outside-r_inside, 2),
                    90, 0, (-angle, r_inside), 0, 90, (r_outside-r_inside, 2),
                    90)
                x, y = vectors.circlepoint(r_outside, math.radians(angle+space))
                self.moveTo(y, r_outside-x, angle+space)
                n -=1
                if n == 0:
                    break
            self.move(2*r_outside, 2*r_outside, move)

    def cosineRule(self, sideA, sideB, angleC):
        return math.sqrt(pow(sideA,2) + pow(sideB,2) - 2*sideA*sideB*math.cos(angleC))

    def straightBottomPlate(self, length, bottomPlateWidth, width, numBulkheads, matingHolesDiam):
        fingerHoles = [ lambda: self.bottomPlateCuts(length, bottomPlateWidth, width, numBulkheads,matingHolesDiam) ]
        self.rectangularWall(length, bottomPlateWidth, "eFeF", callback=fingerHoles, move="up")

    def bottomPlateCuts(self, length, bottomPlateWidth, width, numBulkheads, matingHolesDiam):
        self.plateSlots(length, bottomPlateWidth, width, numBulkheads)
        webThickness = self.thickness*2.0
        edgeOffset = (bottomPlateWidth - width)/2 + self.thickness
        bulkheadGap = length/(numBulkheads+1)
        x = 0
        for i in range(int(numBulkheads) + 1):
            x += bulkheadGap
            self.testleLatticeHole(x,bottomPlateWidth,bulkheadGap,width,edgeOffset,webThickness)
        #tlhx = [lambda: self.testleLatticeHole(x,h,x,h,edgeOffset,webThickness)]

        self.mountingHoles(length, bottomPlateWidth, matingHolesDiam, matingHolesDiam*1.5, 0, (bottomPlateWidth-width)/2.0)

    def mountingHoles(self, x, y, holeDiam, holeOffset, xOffset, yOffset):
        self.hole(x-holeOffset-xOffset, y-holeOffset-yOffset, d=holeDiam)
        self.hole(holeOffset+xOffset, y-holeOffset-yOffset, d=holeDiam)
        self.hole(holeOffset+xOffset, holeOffset+yOffset, d=holeDiam)
        self.hole(x-holeOffset-xOffset, holeOffset+yOffset, d=holeDiam)

    def straightTopPlate(self, length, deckWidth, width, numBulkheads):
        fingerHoles = [ lambda: self.plateSlots(length, deckWidth, width, numBulkheads) ]
        self.rectangularWall(length, deckWidth, "eFeF", callback=fingerHoles, move="up")

    def bulkheadSlots(self, bulkheadGap, height, y=0, numBulkheads=2):
        posx = -0.5 * self.thickness
        for x in range(int(numBulkheads)):
            posx += bulkheadGap + self.thickness
            self.fingerHolesAt(posx, y, height, 90)

    def plateSlots(self, length, plateWidth, width, numBulkheads):
        bulkheadGap = (length-(self.thickness*numBulkheads))/(numBulkheads+1)
        self.edges["h"].settings.setValues(self.thickness, width=2.0)
        self.fingerHolesAt(0, (plateWidth-width)/2.0 - self.thickness, length, 0)
        self.fingerHolesAt(0, plateWidth + self.thickness - ((plateWidth-width)/2.0), length, 0)
        self.edges["h"].settings.setValues(self.thickness, width=1.0)
        self.bulkheadSlots(bulkheadGap, width, ((plateWidth-(width)+self.thickness)/2.0), numBulkheads)

    def sidePlate(self, length, height, numBulkheads):
        self.innersSidePlate(length, height, numBulkheads)
        self.outerSidePlate(length, height, numBulkheads)
    
    def innersSidePlate(self, length, height, numBulkheads):
        bulkheadGap = (length-(self.thickness*numBulkheads))/(numBulkheads+1)
        bulkheadSlots = [lambda: self.bulkheadSlots(bulkheadGap, height, 0, numBulkheads)]
        self.rectangularWall(length, height, "ffff", callback=bulkheadSlots, move="up")

    def outerSidePlate(self, length, height, numBulkheads):
        bulkheadGap = (length-(self.thickness*numBulkheads))/(numBulkheads+1)
        outSidePlateHoles = [lambda: self.outSidePlateHoles(bulkheadGap, height, 0, numBulkheads)]
        
        self.rectangularWall(length, height, "fEfE", callback=outSidePlateHoles, move="up")

    def outSidePlateHoles(self, bulkheadGap, height, y=0, numBulkheads=2):
        holeHeight = height - self.thickness*3.0
        holeWidth = (bulkheadGap - self.thickness)/2
        #posx = -0.5 * self.thickness
        posx = -0.5 * holeWidth - self.thickness
        posy = 0.5 * height
        for x in range(int(numBulkheads+1)):
            posx += holeWidth + self.thickness
            self.rectangularHole(posx, posy, holeWidth, holeHeight)
            posx += holeWidth + self.thickness
            self.rectangularHole(posx, posy, holeWidth, holeHeight)
            #self.fingerHolesAt(posx, y, height, 90)

    def brideSpan(self, length, width, height, deckWidth, matingHolesDiam, numBulkheads=2, centerlineRadius=0, bridgeAngle=0):
        if(centerlineRadius > 0 and bridgeAngle > 0):
            outerRadius = centerlineRadius + (deckWidth/2.0)
            innerRadius = centerlineRadius - (deckWidth/2.0)
            self.moveTo(0, 0)
            innerSpanLength = (math.tau * innerRadius) * (bridgeAngle / 360.0)
            self.rectangularWall(innerSpanLength, height, "efef", move="up")

            self.moveTo(0, 0)
            outerSpanLength = (math.tau * outerRadius) * (bridgeAngle / 360.0)
            self.rectangularWall(outerSpanLength, height, "efef", move="up")

            self.ringSegmentWithEdges(outerRadius, innerRadius, bridgeAngle, move="up")
        else:
            
            # Bridge Bottom Plate
            bottomPlateWidth = (deckWidth - width)/2.0 + width + 2*self.thickness
            self.straightBottomPlate(length, bottomPlateWidth, width, numBulkheads, matingHolesDiam)

            # Bridge Gider Side plates
            for i in range(2):
                self.moveTo(0, 0)
                self.sidePlate(length,height,numBulkheads)

            # Bridge Top Deck Plate
            self.straightTopPlate(length, deckWidth, width, numBulkheads)

        webThickness = edgeOffset = min(width, height)/8.0

        tlhx = [lambda: self.testleLatticeHole(width,height,width,height,edgeOffset,webThickness)]
        # Bridge span end cross member
        for i in range(2):
            self.rectangularWall(width, height, "fFfF", callback=tlhx, move="right")
        # Bridge span internal cross member
        for i in range(2):
            self.rectangularWall(width, height, "ffff", callback=tlhx, move="only left")

        self.rectangularWall(width, height, "ffff", callback=tlhx, move="only up")

        for i in range(int(numBulkheads)):
            self.rectangularWall(width, height, "ffff", callback=tlhx, move="right")
        for i in range(int(numBulkheads)):
            self.rectangularWall(width, height, "ffff", callback=tlhx, move="only left")
        self.rectangularWall(width, height, "ffff", callback=tlhx, move="only up")

    def testleLatticeHole(self, x, y, dx, dy, edgeOffset, webThickness):
        self.testleLatticeHoleHelper(x - dx/2.0, edgeOffset, dx-(2.0*edgeOffset)-webThickness, (dy-2.0*edgeOffset-webThickness)/2.0, "top")
        self.testleLatticeHoleHelper(x - dx/2.0, y-edgeOffset, dx-2.0*edgeOffset-webThickness, -1.0*((dy-2.0*edgeOffset-webThickness)/2.0), "top")
        self.testleLatticeHoleHelper(edgeOffset+x-dx, y/2.0, (dx-2.0*edgeOffset-webThickness)/2.0, dy-2.0*edgeOffset-webThickness, "side")
        self.testleLatticeHoleHelper(x-edgeOffset, y/2.0, -1.0*((dx-2.0*edgeOffset-webThickness)/2.0), dy-2.0*edgeOffset-webThickness, "side")

    def testleLatticeHoleHelper(self, x, y, dx, dy, type):
        """
        Draw a testleLatticeHole

        :param x: position
        :param y: position
        :param dx: width
        :param dy: height
        :param r:  (Default value = 0) radius of the corners
        """
        #            angle beta
        #             ___
        #   {        / | \
        #   {       /  |  \
        # dy{    c /   |   \
        #   {     /    a    \
        #   {    /     |     \
        #   {   |      |      |
        #       +-------------+
        #        ---b---
        #             dx
        #     angle alpha
        #
        #   b = half of dx
        #   a = dy
        #   angle alpha = arctan(a/b)
        #   angle beta = arctan(b/a)
        #   c = sq_rt(a^2 + b^2)
        width = dx
        height = dy
        r = self.thickness

        plateWidth = width/10.0
        plateHeight = height/10.0

        with self.saved_context():
            if type == "top":
                a = height - (plateHeight*2.0)
                b = width/2.0 - plateWidth
                c = math.sqrt(a**2 + b**2)

                alpha = math.degrees(math.atan2(a,b))
                beta = 90 - alpha

                test = alpha + beta

                #print("alpha: ", alpha, " beta: ", beta, " combined: ", test)

                self.moveTo(x, y, 0)
                self.edge(b + plateWidth/2.0)
                self.corner(90, self.burn)
                self.edge(plateHeight)
                self.corner(beta,  self.burn)
                self.edge(c)
                self.corner(alpha,  self.burn)
                self.edge(plateWidth)
                self.corner(alpha,  self.burn)
                self.edge(c)
                self.corner(beta,  self.burn)
                self.edge(plateHeight)
                self.corner(90, self.burn)
                self.edge(b + plateWidth/2.0)

            elif type == "side":
                #print("side")
                a = width - (plateWidth*2.0)
                b = height/2.0 - plateHeight
                c = math.sqrt(a**2 + b**2)

                alpha = math.degrees(math.atan2(a,b))
                beta = 90 - alpha

                test = alpha + beta

                #print("alpha: ", alpha, " beta: ", beta, " combined: ", test)

                self.moveTo(x, y, -90)
                self.edge(b + plateHeight/2.0)
                self.corner(90, self.burn)
                self.edge(plateWidth)
                self.corner(beta,  self.burn)
                self.edge(c)
                self.corner(alpha,  self.burn)
                self.edge(plateHeight)
                self.corner(alpha,  self.burn)
                self.edge(c)
                self.corner(beta,  self.burn)
                self.edge(plateWidth)
                self.corner(90, self.burn)
                self.edge(b + plateHeight/2.0)

    def render(self):
        x, h, bridgeGirderSpan, bridgeGirderHeight, bridgeGirderWidth, bridgeDeckWidth, centerlineRadius, bridgeAngle, edgeOffset, webThickness, numBulkheads,matingHolesDiam = self.x, self.h, self.bridgeGirderSpan, self.bridgeGirderHeight, self.bridgeGirderWidth, self.bridgeDeckWidth, self.centerlineRadius, self.bridgeAngle, self.edgeOffset, self.webThickness, self.numBulkheads, self.matingHolesDiam

        self.brideSpan(bridgeGirderSpan - (2.0*self.thickness), bridgeGirderWidth, bridgeGirderHeight, bridgeDeckWidth, matingHolesDiam, numBulkheads, centerlineRadius, bridgeAngle)

        tlhx = [lambda: self.testleLatticeHole(x,h,x,h,edgeOffset,webThickness)]
        self.rectangularWall(x, h, "eFfF", callback=tlhx, move="right")
        self.rectangularWall(x, h, "eFfF", callback=tlhx, move="up")

        tlhy = [lambda: self.testleLatticeHole(bridgeGirderWidth,h,bridgeGirderWidth,h,edgeOffset,webThickness)]
        self.rectangularWall(bridgeGirderWidth, h, "efff", callback=tlhy, move="left right")
        self.rectangularWall(bridgeGirderWidth, h, "efff", callback=tlhy, move="up")

        xOffset = (x/2) - ( matingHolesDiam + matingHolesDiam*3) 
        mountingHoles = [lambda: self.mountingHoles(x, bridgeGirderWidth, matingHolesDiam, matingHolesDiam*1.5, xOffset, 0)]
        self.rectangularWall(x, bridgeGirderWidth, "FFFF", callback=mountingHoles, move="up")