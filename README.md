# EMLO Site Edit-2
This repository is a re-boot of the software behind the 
[Early Modern Letters Online (EMLO)](http://emlo.bodleian.ox.ac.uk/home) project for the 
[Bodleian Libraries](https://www.bodleian.ox.ac.uk/home) of the University of Oxford. 

More precisely this repository holds a new front-end design of the old one that can be found 
[here](https://github.com/culturesofknowledge/site-edit).

Project resides [here](https://github.com/culturesofknowledge/emlo-project/projects) and a list of relevant documents
can be found [here](https://github.com/culturesofknowledge/emlo-project/wiki/List-of-Documents).

The previous development approach was based on a modular
decoupled (almost) services like approach we are now going for a more 
monolithic style approach.

Dependencies:
* Postgres
* Django 4.0.4

## Uploader
Redesigned in isolation, as a modular piece that would integrate with the "old" code and accessible
[here](https://github.com/J4bbi/emlo_uploader), the code for this is now integrated into the repository as an
[app](https://docs.djangoproject.com/en/4.0/intro/tutorial01/#creating-the-polls-app).