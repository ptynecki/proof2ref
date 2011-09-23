# -*- coding: utf-8 -*-

# proof2ref.py v0.2
# Date: 20.09.2011r
# Author: Piotr Tynecki <piotr@tynecki.pl>

import sys
import os
import linecache
import subprocess

# Set Mizar directory path
mizarPath = "/usr/local/share/mizar/"

copyright = "proof2ref v0.2\nCopyright (C) 2011 by Piotr Tynecki <piotr@tynecki.pl>"

try:
    from lxml import etree
except ImportError:
    print "%s\n\nError:\n\tNo module named lxml. Download from: http://lxml.de/" % copyright
    sys.exit(0)

def runMizf(path):
    """ Generates required files based on the miz file """
    subprocess.call(["accom", path])
    subprocess.call(["verifier", "-q", "-a", path])

def repairXML(path):
    """ Repairs XML file """
    newline = linecache.getline(path, 2)
    newline = newline.replace('mizfiles="%s"' % mizarPath, 'mizfiles="%s"' % mizarPath.replace("/", "&#47;"))

    f = open(path, "rb")
    source = f.readlines()
    f.close()

    f = open(path, "wb")
    source[1] = newline
    f.writelines(source)
    f.close()

def getAllLineNumberFromErrFile(path):
    """ Parses err file """
    path = path.replace("xml", "err")

    f = open(path, "rb")
    source = f.readlines()
    f.close()

    return [x.split()[0] for x in source]

def cleanup():
    """ Removes all files from text directory without miz files """
    currentDirectory = os.listdir("text")
    tempfiles = [x for x in currentDirectory if x.split(".")[1] == "miz"]

    [currentDirectory.remove(x) for x in tempfiles]
    [os.remove("text/%s" % x) for x in currentDirectory]

def replaceProof2Ref(path, XMLpath):
    """ Replaces proofs with references """
    numberOfChanges = [0, []]

    for x, th in enumerate([x for x in etree.parse(XMLpath).findall("JustifiedTheorem")]):
        if x:
            runMizf(path)

        if th.find("SkippedProof") is None:
            proposition = th.find("Proposition")

            nr = proposition.get("nr")
            vid = proposition.get("vid")

            # List of line/col numbers of each proof
            proofsBlock = []

            XML = etree.parse(XMLpath)
            theorems = [theorem for theorem in XML.findall("JustifiedTheorem")]

            mode = 0

            for y in theorems[x + 1:]:
                if y.find("SkippedProof") is None:

                    proof = y.find("Proof")

                    if proof is not None:
                        subProposition = y.find("Proposition")
                        line = subProposition.get("line")
                        col = subProposition.get("col")

                        endProof = proof.find("EndPosition")

                        proofsBlock.append("d%s %d %s %s\niby Th%d\n" % (proof.get("line"), int(proof.get("col")) - 4, endProof.get("line"), endProof.get("col"), x + 1))

                        y.remove(proof)

                        by = etree.Element("By", line = line, col = col)
                        by.append(etree.Element("Ref", nr = nr, vid = vid, line = line, col = col))

                        y.append(by)

                        XML.write(XMLpath, xml_declaration = True, method = "xml")

                        repairXML(XMLpath)

                        mode = 1

            if mode:
                subprocess.call(["nice", "-n", "19", "verifier", "-q", "-c", XMLpath])

                # Correct references list
                correctRef = [x for x in proofsBlock if x.split()[0][1:] not in getAllLineNumberFromErrFile(XMLpath)]

                if correctRef:
                    numberOfChanges[0] += len(correctRef)
                    numberOfChanges[1].append(correctRef)

                    for numbers in correctRef:
                        edt = open(XMLpath.replace("xml", "edt"), "ab")
                        edt.write(numbers)
                        edt.close()

                    # Calls the process which updates miz file
                    subprocess.call(["accom", "-p", path])
                    subprocess.call(["edtfile", path])
                    subprocess.call(["mv", "-f", "%s$-$" % path[:-3], path])

        cleanup()

    return numberOfChanges

def createReport(score):
    """ Creates report of changes about each miz file """
    for x in score:
        if x[1][0] > 0:
            r = open("report.txt", "ab")
            r.write("Filename: %s\nNumber of changes: %s\n" % (x[0], x[1][0]))

            for y in x[1][1]:
                r.write("\t%s\n" % y[0][:-1].replace("\n", "\n\t"))

            r.write("\n")
            r.close()

def main(score, path, XMLpath):
    """ Runs the main procedures """
    runMizf(path)
    score.append((path.split("/")[-1], replaceProof2Ref(path, XMLpath)))
    cleanup()

if __name__=="__main__":
    argcount = len(sys.argv)

    score = []

    os.system("clear")

    # For a single *.miz file
    if argcount > 2 and sys.argv[1] == "-f":
        try:
            path = "%s.miz" % sys.argv[2]
            XMLpath = path.replace("miz", "xml")

            if not os.path.exists(path):
                raise IOError

            main(score, path, XMLpath)

        except IOError:
            print "%s\n\nError:\n\tFile %s is corrupted or doesn't exist" % (copyright, sys.argv[2])

        finally:
            os.system("clear")

    # For all the *.miz files from a text directory
    elif argcount > 2 and sys.argv[1] == "-d":
        try:
            directory = os.listdir(sys.argv[2])

            for x in directory:
                path = "%s/%s" % (sys.argv[2], x)
                XMLpath = path.replace("miz", "xml")

                main(score, path, XMLpath)

        except OSError:
            print "%s\n\nError:\n\tDirectory %s doesn't exist" % (copyright, sys.argv[2])

        except IOError:
            print "%s\n\nError:\n\tFile %s is corrupted or doesn't exist" % (copyright, path)

        finally:
            os.system("clear")

    else:
        print "%s\n\nExamples:\n\tpython proof2ref.py -f text/filename\n\tpython proof2ref.py -d text\n\nExtras:\n\tCreates report of changes about single/each miz file\n\tpython proof2ref.py -f text/filename -r\n\tpython proof2ref.py -d text -r" % copyright

    if argcount > 3 and sys.argv[3] == "-r":
        createReport(score)
