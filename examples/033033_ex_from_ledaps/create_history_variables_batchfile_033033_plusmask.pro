retall

;this batchfile will create history variables from the segmentation and ftv outputs

;enter the paths to diag.sav files created during segmentation to indicate which
;segmentation runs you want to create history variables for 

diagfile = ['/vol/v1/scenes/033033/outputs/nbr/LT_v2.1_nbr_033033_paramset01_20160303_140513_diag.sav'] ;full path to dia.sav files - can include multiple files, use a comma to separate them
template_headerfile = '/vol/v1/general_files/helperfiles/mrlc_template_headerfile.hdr'
recovery_mask_override = '/vol/v1/scenes/033033/outputs/nbr/nbr_lt_labels_mr227/LT_v2.1_nbr_033033_paramset01_20160303_140513_greatest_recovery_mmu11_loose.bsq'

;#####################################################################################
;only update pixels in dist/rec mask
; FOR MASKS ADD: ', maskyes = 1, recovery_mask_override=recovery_mask_override'

create_history_variables, diagfile, template_headerfile , maskyes = 1, recovery_mask_override=recovery_mask_override
