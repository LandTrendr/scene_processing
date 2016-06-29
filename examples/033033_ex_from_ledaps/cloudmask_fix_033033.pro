retall
;this batchfile is used to create a automatic cloudmasks based either on spectral data from given image dates or
;from difference-from-cloud-free condition images

;---please state the landsat path/row ID and path to the data as described following each variable---
ppprrr = '033033' ; ex. '046026' -MUST BE PPP (path) and RRR (row), three digits for both path and row, use zero if needed ex: '0PP0RR'
path = '/vol/v1/scenes/033033/' ; ex. 'F:\046026\' -MAKE SURE THERE IS A "\" AT THE END, must point to a drive path, even if on a server
template_header = "/vol/v1/general_files/helperfiles/mrlc_template_headerfile.hdr" ;give the full path to a template projection header (.hdr) file

;select method 1: thresholds clouds\shadows based on image bands fixing method
cldmsk_fix_method = [1]

;for best results near-yearly time steps should be used and the images should be either cloud\haze-free
;or have really good cloudmasks

cldmsk_ref_dates = 1984238 ;example: [1985211,1986215,1992202]
;enter the year day ids of the cloudmasks that require manual fixing
fix_these_dates = 1984222 ;example: [1985211] or [1985211,1986215] 



;#######################################################################################################################
params = {ppprrr:ppprrr,$
  path:path,$
  cldmsk_fix_method:cldmsk_fix_method,$
  cldmsk_ref_dates:cldmsk_ref_dates,$
  fix_these_dates:fix_these_dates,$
  template_header:template_header}
  
fix_cloudmask_processor, params