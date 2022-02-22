dremel_layers = []
file_location = ""
section = ""

section_type = section.upper()
#layer number in gcode
layers = [x-1 for x in dremel_layers]
gcode = open(file_location, 'r')
gcode_lines = gcode.readlines()
for j in range(len(layers)):
#   find the start of the layer that will be removed
    layer = gcode_lines.index(';LAYER:' + str(layers[j]) + '\n')
#    find section
    for i in range(layer, len(gcode_lines)):
        if ';TYPE:'+section_type+'\n' in gcode_lines[i]:
            section_num = i
#            find last E value to keep, look backwards from the section layer of interest
            for k in reversed(range(section_num)):
                if 'E' in gcode_lines[k]:
                    temp_E = gcode_lines[k].find("E")
                    E1 = gcode_lines[k][temp_E+1:len(gcode_lines[k])-1]
                    break
#            find last E to remove, start looking from beginning of next section and search backwards
            for m in range(section_num+1, len(gcode_lines)):
                if ';' in gcode_lines[m]:
                    section_num_plus1 = m
                    for z in reversed(range(section_num_plus1)):
                        if 'E' in gcode_lines[z]:
                            temp_E = gcode_lines[z].find("E")
                            E2 = gcode_lines[z][temp_E + 1:len(gcode_lines[z]) - 1]
                            break
                    break
            break
#    replace E values
    E_remove = float(E2) - float(E1)
    for n in range(section_num, len(gcode_lines)):
        if 'G1' in gcode_lines[n]:
            temp_E = gcode_lines[n].find("E")
#            ideally copy old E value, comes up with letters with code at the bottom
            E_str = gcode_lines[n][temp_E+1:len(gcode_lines[n])-1]
#            string without E value
            str_wo_E = gcode_lines[n][:temp_E+1]
#           prevent the E code at the bottom of the script from changing
            if not E_str.isupper():
                #calculate new E value
                E_replace = round(float(E_str)-E_remove, 5)
                #delete previous line of code
                del gcode_lines[n]
                #add back line of code with new E value
                gcode_lines.insert(n, str_wo_E+str(E_replace)+"\n")
    del gcode_lines[section_num + 1:section_num_plus1]


with open(file_location.rsplit(".", 1)[0]+" v2pyedit.txt", 'w') as output:
    for row in gcode_lines:
        output.write(str(row))
with open(file_location.rsplit(".", 1)[0]+" v2pyedit.gcode", 'w') as output:
    for row in gcode_lines:
        output.write(str(row))

Z_val = [0.1]
Z_pos = 1
for q in range(len(gcode_lines)):
    if 'Z' in gcode_lines[q]:
        temp_Z = gcode_lines[q].find("Z")
        Z_str = gcode_lines[q][temp_Z + 1:len(gcode_lines[q]) - 1]
        if not Z_str.isupper():
            Z_val.append(float(Z_str))
            if Z_val[Z_pos] < Z_val[Z_pos - 1]:
                print("\nWARNING: Z values not always increasing (assuming Medium Quality)")
                gcode.close()
                exit(1)
            if not round(Z_val[Z_pos] - Z_val[Z_pos - 1], 1) == 0.2:
                print("\nWARNING: Z values not increasing at the same rate (assuming Medium Quality)")
                gcode.close()
                exit(1)
            Z_pos = Z_pos+1
print("\nZ values always increasing at the same rate (assuming Medium Quality)")
gcode.close()

##NOTES
#E value decreases after each layer is finished printing which indicates the retraction of filament
#if the layer is simple (ex. just a wall)
#   there will be E0 code that traces the perimeter presumibly so that filament can cool
