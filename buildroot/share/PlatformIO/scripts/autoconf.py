def lineHasKey(line, key):
  return "#define "+key+" " in line or "#define "+key+"\n" in line.lstrip()

def opt_enable(key):
  filenames = ["Marlin/Configuration.h", "Marlin/Configuration_adv.h"]
  for filename in filenames:
    tmp = open(filename+"~", "wt")
    matched = False
    with open(filename, "rt") as input:
      for line in input:
        if lineHasKey(line, key):
          matched = True
          line = line.replace("// #define", "//#define",1).replace("//#define", "#define",1)
        tmp.write(line)
    tmp.close()
    if matched is True:
      os.rename(filename+"~", filename)
    else:
      os.unlink(filename+"~")

def opt_disable(key):
  filenames = ["Marlin/Configuration.h", "Marlin/Configuration_adv.h"]
  for filename in filenames:
    tmp = open(filename+"~", "wt")
    matched = False
    with open(filename, "rt") as input:
      for line in input:
        if lineHasKey(line, key):
          matched = True
          line = line.replace("#define", "//#define",1).replace("////#define", "//#define",1)
        tmp.write(line)
    tmp.close()
    if matched is True:
      os.rename(filename+"~", filename)
    else:
      os.unlink(filename+"~")

def opt_set(key, value):
  filenames = ["Marlin/Configuration.h", "Marlin/Configuration_adv.h"]
  matched = False
  for filename in filenames:
    tmp = open(filename+"~", "wt")
    with open(filename, "rt") as input:
      for line in input:
        if lineHasKey(line, key):
          matched = True
          line = line.replace("// #define", "//#define").replace("//#define", "#define").replace(key, key+" "+value+" //", 1)
        tmp.write(line)
    tmp.close()
    if matched is True:
      os.rename(filename+"~", filename)
      break
  if matched is False:
    with open("Marlin/Configuration.h", "at") as input:
      input.write("\n#define "+key+" "+value)

def pio_update_env(value):
  filename = "platformio.ini"
  tmp = open(filename+"~", "wt")
  matched = False
  with open(filename, "rt") as input:
    for line in input:
      if line.startswith("default_envs ="):
        tmp.write("#"+line)
        tmp.write("default_envs = "+value+"\n")
      else:
        tmp.write(line)
  tmp.close()
  os.rename(filename+"~", filename)


import pioutil
if pioutil.is_pio_build():
  import configparser
  import glob
  import itertools
  import os
  import string
  Import("env")

  filenames = glob.glob("config*.ini")
  config = configparser.RawConfigParser()
  config.optionxform = lambda option: option
  for filename in filenames:
    with open(filename) as fp:
      config.read_file(itertools.chain(['[marlin]'], fp), source=filename)
  for key, value in config.items('marlin'):
    if key.upper() == "MOTHERBOARD_ENV":
      print("UPDATING PLATFORMIO ENV")
      pio_update_env(value)
      env.Append(
          CPPDEFINES=[("default_envs", value)],
      )
    if value == "true":
      print("ENABLE", key)
      opt_enable(key)
    elif value == "false":
      print("DISABLE", key)
      opt_disable(key)
    else:
      print("SET", key, value)
      opt_set(key, value)