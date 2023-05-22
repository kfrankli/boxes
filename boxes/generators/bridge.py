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
        self.buildArgParser(x=70, y=70, h=150)
        self.argparser.add_argument(
            "--bridgeGirderSpan",  action="store", type=float, default=300,
            help="Length of the Bridge Girder Span in mm. Ignored if bridgeAngle and centerlineRadius are set. LGB10000=300 LGB10600=600 LGB10610=1200")
        self.argparser.add_argument(
            "--bridgeGirderHeight",  action="store", type=float, default=30,
            help="Length of the Bridge Girder Height")
        self.argparser.add_argument(
            "--bridgeGirderWidth",  action="store", type=float, default=110,
            help="Length of the Bridge Girder Width")
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
            "--webThickness",  action="store", type=float, default=5,
            help="thickness of webbing")
        self.argparser.add_argument(
            "--numBulkheads",  action="store", type=float, default=2,
            help="number of Bulkheads")

    def xSlots(self, blukheadGap, numBulkhead=2):
        posx = -0.5 * self.thickness
        for x in range(numBulkhead):
            posx += bulkheadGap + self.thickness
            posy = 0
            for y in self.sy:
                self.fingerHolesAt(posx, posy, y)
                posy += y + self.thickness

    def brideSpan(self, length, width, height, numBulkheads=2, centerlineRadius=0, bridgeAngle=0):
        print(length, width, height)
        if(centerlineRadius > 0 and bridgeAngle > 0):
            outerRadius = centerlineRadius + (width/2.0)
            innerRadius = centerlineRadius - (width/2.0)
            print(outerRadius, innerRadius, bridgeAngle)

            self.moveTo(0, 0)
            innerSpanLength = (math.tau * innerRadius) * (bridgeAngle / 360.0)
            self.rectangularWall(innerSpanLength, height, "efef", move="up")

            self.moveTo(0, 0)
            outerSpanLength = (math.tau * outerRadius) * (bridgeAngle / 360.0)
            self.rectangularWall(outerSpanLength, height, "efef", move="up")

            self.parts.ringSegment(outerRadius, innerRadius, bridgeAngle, move="up")
        else:
            bulkheadGap = length/numBulkheads
            for i in range(2):
                self.moveTo(0, 0)
                self.rectangularWall(length, height, "efef", move="up")


        webThickness = edgeOffset = min(width, height)/8.0

        tlhx = [lambda: self.testleLatticeHole(width,height,width,height,edgeOffset,webThickness)]
        for i in range(2):
            self.rectangularWall(width, height, "fFfF", callback=tlhx, move="right")
        for i in range(2):
            self.rectangularWall(width, height, "ffff", callback=tlhx, move="only left")
        self.rectangularWall(width, height, "ffff", callback=tlhx, move="only up")

        for i in range(int(numBulkheads)):
            self.rectangularWall(width, height, "ffff", callback=tlhx, move="right")
        for i in range(int(numBulkheads)):
            self.rectangularWall(width, height, "ffff", callback=tlhx, move="only left")
        self.rectangularWall(width, height, "ffff", callback=tlhx, move="only up")
        for i in range(int(numBulkheads) + 1):
            #testleLatticeHole
            print("Test")



    def testleLatticeHole(self, x, y, dx, dy, edgeOffset, webThickness):
        self.testleLatticeHoleHelper(x/2.0, edgeOffset, dx-(2.0*edgeOffset)-webThickness, (dy-2.0*edgeOffset-webThickness)/2.0, "top")
        self.testleLatticeHoleHelper(x/2.0, y-edgeOffset, dx-2.0*edgeOffset-webThickness, -1.0*((dy-2.0*edgeOffset-webThickness)/2.0), "top")
        self.testleLatticeHoleHelper(edgeOffset, y/2.0, (dx-2.0*edgeOffset-webThickness)/2.0, dy-2.0*edgeOffset-webThickness, "side")
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
        x, y, h, bridgeGirderSpan, bridgeGirderHeight, bridgeGirderWidth, centerlineRadius, bridgeAngle, edgeOffset, webThickness, numBulkheads = self.x, self.y, self.h, self.bridgeGirderSpan, self.bridgeGirderHeight, self.bridgeGirderWidth, self.centerlineRadius, self.bridgeAngle, self.edgeOffset, self.webThickness, self.numBulkheads

        self.brideSpan(bridgeGirderSpan, bridgeGirderWidth, bridgeGirderHeight, numBulkheads, centerlineRadius, bridgeAngle)

        tlhx = [lambda: self.testleLatticeHole(x,h,x,h,edgeOffset,webThickness)]
        tlhy = [lambda: self.testleLatticeHole(y,h,y,h,edgeOffset,webThickness)]

        self.rectangularWall(x, h, "efef", callback=tlhx, move="right")
        self.rectangularWall(x, h, "eFeF", callback=tlhx, move="up")
        self.rectangularWall(y, h, "efef", callback=tlhy, move="left right")
        self.rectangularWall(y, h, "eFeF", callback=tlhy, move="up")
