dremel_layers = [2,4,5]
file_location = "E:\D3_solid in cylinder.txt"

#layer number in gcode
layers = [x-1 for x in dremel_layers]
gcode = open(file_location, 'r')
gcode_lines = gcode.readlines()
for j in range(len(layers)):
#   find the start of the layer above the skin section that will be removed
    layer_plus1 = gcode_lines.index(';LAYER:' + str(layers[j] + 1) + '\n')
#    find skin section
    for i in reversed(range(layer_plus1)):
        if ';TYPE:SKIN\n' in gcode_lines[i]:
            skin_num = i
#            find last E value to keep, look backwards from the skin layer of interest
            for k in reversed(range(skin_num)):
                if 'E' in gcode_lines[k]:
                    temp_E = gcode_lines[k].find("E")
                    E1 = gcode_lines[k][temp_E+1:len(gcode_lines[k])-1]
                    print("E1: "+E1)
                    break
#            find last E to remove, start looking from beginning of next section and search backwards
            for m in reversed(range(layer_plus1 - 2)):
                if 'E' in gcode_lines[m]:
                    temp_E = gcode_lines[m].find("E")
                    E2 = gcode_lines[m][temp_E+1:len(gcode_lines[m])-1]
                    print(E2)
                    break
            break
#    replace E values
    E_remove = float(E2) - float(E1)
    for n in range(skin_num, len(gcode_lines)):
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
    del gcode_lines[skin_num + 1:layer_plus1 - 1]

with open(file_location.rsplit(".", 1)[0]+" pyedit.txt", 'w') as output:
    for row in gcode_lines:
        output.write(str(row))
with open(file_location.rsplit(".", 1)[0]+" pyedit.gcode", 'w') as output:
    for row in gcode_lines:
        output.write(str(row))

Z_val = [0]
Z_pos = 1
for q in range(len(gcode_lines)):
    if 'Z' in gcode_lines[q]:
        temp_Z = gcode_lines[q].find("Z")
        Z_str = gcode_lines[q][temp_Z + 1:len(gcode_lines[q]) - 1]
        if not Z_str.isupper():
            Z_val.append(float(Z_str))
            if Z_val[Z_pos] < Z_val[Z_pos - 1]:
                print("Z values not always increasing")
                gcode.close()
                exit(1)
            Z_pos = Z_pos+1
print("Z values always increasing")
gcode.close()

##NOTES
#E value decreases after each layer is finished printing which indicates the retraction of filament
#if the layer is simple (ex. just a wall)
#   there will be E0 code that traces the perimeter presumibly so that filament can cool