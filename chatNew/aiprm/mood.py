mood = '''<option value="" selected="">Default</option>

          
            <option value="2001">
              Authoritative
              </option> 
          
            <option value="2002">
              Clinical
              </option> 
          
            <option value="2003">
              Cold
              </option> 
          
            <option value="2004">
              Confident
              </option> 
          
            <option value="2005">
              Cynical
              </option> 
          
            <option value="2006">
              Emotional
              </option> 
          
            <option value="2007">
              Empathetic
              </option> 
          
            <option value="2008">
              Formal
              </option> 
          
            <option value="2009">
              Friendly
              </option> 
          
            <option value="2010">
              Humorous
              </option> 
          
            <option value="2011">
              Informal
              </option> 
          
            <option value="2012">
              Ironic
              </option> 
          
            <option value="2013">
              Optimistic
              </option> 
          
            <option value="2014">
              Pessimistic
              </option> 
          
            <option value="2015">
              Playful
              </option> 
          
            <option value="2016">
              Sarcastic
              </option> 
          
            <option value="2017">
              Serious
              </option> 
          
            <option value="2018">
              Sympathetic
              </option> 
          
            <option value="2019">
              Tentative
              </option> 
          
            <option value="2020">
              Warm
              </option> 
          
        </select>'''
mood,lsMood = mood.split('">\n'),[]
for k in range(1,len(mood)):
  lsMood.append(mood[k].replace(' ','').split('\n</option>')[0])
input(lsMood)
