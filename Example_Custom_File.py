## This is the general format for a custom mask.
# The function that interprets this custom mask is:
#
#elif mask_type == 'custom':
#            with open(kwargs['file'], 'r') as f:
#                mask_func_str = f.read()
#                #print(mask_func_str)
#            namespace = {"np": np}
#            exec(mask_func_str, namespace)
#            mask_func = namespace["custom"]
#            mask = mask_func(shape)
#
# This function defines a namespace 'custom' and executes the code below. 
# as far as I can tell, the only restrictions on this code is that you must
# define all variables explicitly, and you **must** keep the function name 'custom'.
# Finally, of course, you must return the mask to the calling function, which will
# be passed to the masker function and produce your plots. 
# You can import various libraries, should you need them. 
# Errors are printed to the error box.


#required:
def custom(shape):

    # customizable:
    import numpy as np
    height = 50
    width = 50 
    mask = np.zeros(shape)
    rows, cols = shape
    left = (cols - width) // 2
    right = left + width
    top = (rows - height) // 2
    bottom = top + height
    mask[:top, :] = 1
    mask[bottom:, :] = 1
    mask[:, :left] = 1
    mask[:, right:] = 1

    #required:
    return mask