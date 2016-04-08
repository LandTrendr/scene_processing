;This batch file controls all of the ledaps landtrendr preprocessing steps
;inputs: diag, label_param, class_code

;#####################################################################################################
;
;landtrendr post-segmentation change labeling\map creation and spatial filter and patch aggregation 
;
;#####################################################################################################


;-------------inputs-------------
;full path to the diag.sav files in the outputs folder that you want to run labeling and filter on
diag_files='/vol/v1/scenes/033033/outputs/nbr/LT_v2.1_nbr_033033_paramset01_20160303_140513_diag.sav' ;diag file, find is diff

;full path to label parameter .txt files.  these correspond to the above daig_files so one must exist
;for for each, they do not have to be the same, but can be     
label_parameters_txt='/vol/v1/general_files/helperfiles/mr227_nbr_label_parameters.txt' ;nbr, band5

;full path to a single class code file that defines what map outputs will be created    
class_code_txt = '/vol/v1/general_files/helperfiles/generic_label_codes.txt'

;full path to a projection template file  
templatehdr = '/vol/v1/general_files/helperfiles/mrlc_template_headerfile.hdr' ;same

;-------------run the program------------- 
run_lt_label_and_filtering, diag_files, label_parameters_txt, class_code_txt, templatehdr 