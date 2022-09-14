# MEMS-SIM
This repository is under construction and currently in development.

In the folders are details about the material list and costs to build a MEMS-SIM microscope as described in this BioRxiv preprint:  [https://www.biorxiv.org/content/10.1101/2022.09.12.507543v1](https://www.biorxiv.org/content/10.1101/2022.09.12.507543v1) 

Additionally there are 3D-designs, a basic control code specifically tailored to the MEMS used for the microscope and electronics diagram for the control.

## MEMS-SIM design
The below 3D-schematic shows the overall setup, excluting the lasers and sample stage.

![3D design overview](https://user-images.githubusercontent.com/96420893/190105034-b82ab142-a266-4d94-a616-d9037ce25105.png)

The 3D parts and full assembly of the shown setup are available in Autodesk Inventor format under the [3D design MEMS-SIM folder]

## Part list
The part list and costs (accurate as of September 2022) can be found in [this pdf](https://github.com/RalfBauerUoS/MEMS-SIM/blob/3ace88392d8fb00135eca98648ba5507b43cb822/MEMS-SIM%20-%20component%20list%20and%20costs.pdf)

## Electronics
An overview schematics of the electronics required to drive the two MEMS micromirror of the MEMS-SIM setup can be found [here](https://github.com/RalfBauerUoS/MEMS-SIM/blob/3ace88392d8fb00135eca98648ba5507b43cb822/Electronics/MEMS-SIM_Electronics_overview.png).

## MEMS control
The tip, tilt and piston movement and positioning of the two MEMS micromirror is controlled using an Arduino micro and custom python code with GUI. Both can be found in the relevant sub-folder.
