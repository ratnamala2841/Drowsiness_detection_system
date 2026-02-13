from roboflow import Roboflow
rf = Roboflow(api_key="sjPE4Yl33Ooq27uzGWa5")
project = rf.workspace("computer-vision-workspace-uyi5g").project("nthuddd-m8y1k")
version = project.version(1)
dataset = version.download("yolov8")
                