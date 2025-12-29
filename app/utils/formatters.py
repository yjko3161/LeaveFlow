def num_to_kor(num):
    if num is None:
        return "영"
    
    units = ['', '만', '억', '조']
    small_units = ['', '십', '백', '천']
    num_str = str(num)
    length = len(num_str)
    result = []
    
    # Reverse to process from ones
    num_str_rev = num_str[::-1]
    
    for i in range(0, length, 4):
        chunk = num_str_rev[i:i+4]
        chunk_res = []
        for j, digit in enumerate(chunk):
            n = int(digit)
            if n > 0:
                chunk_res.append(small_units[j])
                # Convert digit to hanja-like hangul? 
                # Usually: 일, 이, 삼, 사...
                # But for '십', '백', '천', we often omit '일' (e.g. 일십 -> 십), but '일금' format usually keeps it or omits it.
                # Standard: 일금 일십삼만... (130,000)
                # Let's use explicit mapping
                kor_digit = "영일이삼사오육칠팔구"[n]
                if j > 0 and n == 1:
                    # For 10, 100, 1000, usually '일' is omitted in spoken, but in formal writing '일' is often kept or omitted depending on convention.
                    # Image shows "일금 삼십오만...". 35 -> 삼십오.
                    # 13 -> 십삼 or 일십삼? 
                    # Let's keep it simple: always include digit unless it is clean enough.
                    pass
                chunk_res.append(kor_digit)
        
        if chunk_res:
            # Reverse chunk back
            chunk_res = chunk_res[::-1]
            # Replace digit+unit (e.g. 1+십 -> 일십)
            # Refine: if digit is 1 and unit exists, remove 1? 
            # "일십" vs "십". Formal documents often use "일십". 
            # Let's try standard korean package logic or simplified.
            
            # Simplified approach: Just map digit -> kor
            
            result.append(units[i//4])
            result.append("".join(chunk_res))
            
    # This logic is getting messy. Let's use a simpler known algorithm.
    
    # Re-do with clean logic
    return _convert_to_korean(num)

def _convert_to_korean(num):
    if num == 0: return "영"
    
    digits = "영일이삼사오육칠팔구"
    units = ["", "십", "백", "천"]
    big_units = ["", "만", "억", "조"]
    
    s_num = str(num)
    length = len(s_num)
    result = []
    
    # Split into 4-digit chunks
    for i, chunk in enumerate(reversed([s_num[max(0, length-4*(i+1)):length-4*i] for i in range((length-1)//4 + 1)])):
        if int(chunk) == 0: continue
        
        chunk_res = ""
        for j, digit in enumerate(chunk):
            n = int(digit)
            if n > 0:
                # Digit char
                # If 1 at 10/100/1000 position, typically omit '일' in casual, but '일금' formatting usually likes explicit '일금 일십...' or just '일금 십...'
                # Image: "일금 삼십오만육천오백원" -> 356,500.
                # 3 -> 삼, 5 -> 오.
                # Let's include digit char always for now, then can strip '일' from '일십' if prefer.
                # Actually "일십" is very formal. "십" is common. 
                # Let's use simple mapping first.
                chunk_res += digits[n] + units[len(chunk)-1-j]
            
        # Clean up: remove '일' from '일십', '일백', '일천' if desired.
        # But '일만', '일억' usually keeps '일' if it is just 10000.
        # Let's keep '일' for precision as this is financial.
        
        if chunk_res:
             result.append(chunk_res + big_units[len(big_units)-1-i if (len(big_units)-1-i) < len(big_units) else 0]) # FIX INDEX
             
    # This is hard to write from scratch error-free in one go.
    # Let's implement a robust version.
    
    # Version 3
    num_str = str(num)
    result = ""
    unit_pos = 0
    
    while num > 0:
        chunk = num % 10000
        if chunk > 0:
            chunk_str = ""
            # Process 4 digits
            c_units = ["", "십", "백", "천"]
            c_val = chunk
            c_idx = 0
            while c_val > 0:
                d = c_val % 10
                if d > 0:
                    chunk_str = digits[d] + c_units[c_idx] + chunk_str
                c_val //= 10
                c_idx += 1
            result = chunk_str + big_units[unit_pos] + result
        num //= 10000
        unit_pos += 1
        
    return result

