
# combinations = ['set_dpi-convert_to_grayscale', 'set_dpi-increase_contrast-convert_to_grayscale', 'set_dpi-convert_to_grayscale-remove_noise', 'set_dpi-increase_contrast-convert_to_grayscale-remove_noise', 'set_dpi-convert_to_grayscale-deskew', 'set_dpi-increase_contrast-convert_to_grayscale-deskew', 'set_dpi-convert_to_grayscale-remove_noise-deskew', 'set_dpi-increase_contrast-convert_to_grayscale-remove_noise-deskew']
combinations = ['set_dpi-increase_contrast-increase_sharpness-remove_noise']

for image in glob.glob('images2\\*'):
    filename = os.path.split(image)[-1].split('.jpg')[0]
    preproc_image = 'preprocessed2\\'+filename+'.jpg'
    shutil.copy(image, preproc_image)
    for combination in combinations:
        methods = combination.split('-')
        for method in methods:
            if 'deskew' in method:
                preproc_image = eval(method+'(preproc_image)')
            else:
                preproc_image = eval(method+'(preproc_image, preproc_image)')
        # print(combination)
        image_name = filename+'_'+combination+'.jpg'
        img = cv2.imread(preproc_image)
        cv2.imwrite(preproc_image, img)

        parsed_output = 'preprocessed2\\'+filename+'_'+combination
        command = 'tesseract {} {} -l eng --psm 4'.format(preproc_image, parsed_output)
        os.system(command)
