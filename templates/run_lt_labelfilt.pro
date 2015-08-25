;This batch file controls all of the ledaps landtrendr preprocessing steps
;inputs: diag, label_param, class_code

;#####################################################################################################
;
;landtrendr post-segmentation change labeling\map creation and spatial filter and patch aggregation 
;
;#####################################################################################################


;-------------inputs-------------
;full path to the diag.sav files in the outputs folder that you want to run labeling and filter on
diag_files='{{diagFile}}' ;diag file, find is diff

;full path to label parameter .txt files.  these correspond to the above daig_files so one must exist
;for for each, they do not have to be the same, but can be     
label_parameters_txt='{{labelTxt}}' ;nbr, band5

;full path to a single class code file that defines what map outputs will be created    
class_code_txt = '{{classTxt}}'

;full path to a projection template file  
templatehdr = '{{templateHdr}}' ;same

;-------------run the program------------- 
run_lt_label_and_filtering, diag_files, label_parameters_txt, class_code_txt, templatehdr 
