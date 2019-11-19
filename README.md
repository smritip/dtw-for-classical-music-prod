# Using Dynamic Time Warping to Improve the Classical Music Production Workflow

This GitHub repository maintains the source code for the project: Using Dynamic Time Warping to Improve the Classical Music Production Workflow. This work comes from a Master’s thesis project from the Music Technology Lab at the Massachusetts Institute of Technology (MIT). The thesis can be found [here](http://musictech.mit.edu/sites/default/files/documents/pramanick_meng.pdf), and the following is a summary of the project:

The current music production workflow, comprising recording, editing, mixing, and mastering music, requires a great deal of manual work for the sound engineer. This thesis aims to bring some recent advances in Music Information Retrieval (MIR) techniques to music production tools, with the goal of streamlining the current process followed by sound engineers. We explored all areas in the music production workflow (with a focus on classical music) that could benefit from digital signal processing (DSP) and MIR-based tools, built and iterated on these tools, and transformed the tools into products that are beneficial and easy to use.

We collaborated with the Boston Symphony Orchestra (BSO) sound engineers to gather requirements for this work, which led to the identification of our two tools: an automatic marking transfer (AMT) system and an audio search (AS) system, which each use the Dynamic Time Warping (DTW) algorithm. We then collaborated with other potential users for both AMT and AS tools, including sound engineers from radio stations in the Boston area. This enabled us to identify additional workflows and finalize requirements for these tools. Based on these, we created successful standalone applications for AMT and AS.

## What is in this repository?

This repository maintains the code for:
* the underlying algorithms for AMT and AS (DTW for Audio Synchronization and Audio Matching),
* the scripts to run the AMT and AS standalone Python applications, and
* the respective Windows executables for the apps (found in ``dist"), which require no installation of Python.

AMT Application: 
![AMT](https://drive.google.com/file/d/1LGwOj3rNnUaLPtsDLCqi1u5KaePmYVZT/view?usp=sharing "AMT")

AS Application: 
![AS](https://drive.google.com/file/d/1yal8LxXWKOdIY1AEfnNigYZst7fSHR1z/view?usp=sharing "AS")

