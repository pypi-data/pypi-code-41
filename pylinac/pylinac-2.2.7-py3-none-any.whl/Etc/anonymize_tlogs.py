"""Anonymize trajectory logs (.bin and .txt files) by replacing the first set of values to `anonymized` in the file name,
 as well as replacing the `Patient ID` tag in the .txt file."""
import os
import os.path as osp

cwd = osp.dirname(osp.realpath(__file__))

for file in os.listdir(cwd):
    # replace file title with anonymized
    if file.endswith('.bin') or file.endswith('.txt'):
        old_path = osp.join(cwd, file)
        mrindex = file.find('_')
        if mrindex > 0:
            new_filename = 'anonymized' + file[mrindex:]
            new_path = osp.join(cwd, new_filename)
            os.rename(old_path, new_path)

        # replace Patient ID tag with anonymized
        if new_path.endswith('.txt'):
            txtpath = osp.join(cwd, new_path)
            with open(txtpath) as txtfile:
                txtdata = txtfile.readlines()
            for idx, line in enumerate(txtdata):
                if line.startswith('Patient ID'):
                    colonidx = line.find(':')
                    newline = line[:colonidx] + ':\tAnonymous\n'
                    txtdata[idx] = newline
                    ttt = 1
            with open(txtpath, mode='w') as txtfile:
                txtfile.writelines(txtdata)





