 
 
   
   """
   Error Codes:
   1. Charging Completed Successfully
   2. Power meter not working
   3. Insufficient Balance
   4. Invalid ID
   5. Any other error
   """ 
 
        
def check_rfid_valid(idtag_str):
    global start_time
    print(f"Charger: Input give Validation started")
    print(f"Charger: data being sent")
    global serial_q
    read_string = ""
    ser_com.write(("wisun socket_write 4 \""+idtag_str + "\"\n").encode())
    print("Charger: wisun socket_write 4 \""+idtag_str + "\"\n")
    
    if serial_q:
        read_string = serial_q.pop()
    
    while "valid" not in str(read_string):
        if serial_q:
            read_string = serial_q.pop()
        else:
            continue
        print("\r", f"Charger: waiting For Id validation", end='\r')
    print(f"Charger: Validation done")

    if "valid_yes" in str(read_string):
        return True
    elif "valid_not" in str(read_string):
        return False
    elif"valid_insuff" in str(read_string):
        return "Low balance"
    elif"valid_error" in str(read_string):
        return "Onem2m Not responding at the Moment"
