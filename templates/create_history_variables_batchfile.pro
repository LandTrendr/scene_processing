retall

;this batchfile will create history variables from the segmentation and ftv outputs

;enter the paths to diag.sav files created during segmentation to indicate which
;segmentation runs you want to create history variables for 

diagfile = ['{{diagFile}}'] ;full path to dia.sav files - can include multiple files, use a comma to separate them
template_headerfile = '{{templateHdr}}'
recovery_mask_override = '{{maskFile}}'

;#####################################################################################
;only update pixels in dist/rec mask
; FOR MASKS ADD: ', maskyes = 1, recovery_mask_override=recovery_mask_override'

create_history_variables, diagfile, template_headerfile {{withMaskInputs}}

