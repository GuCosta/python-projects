# Windows Management Instrumentation
# to get system Information
import wmi # pip install wmi

c = wmi.WMI() # connect to the local machine

# a WMI query always returns a list
my_system = c.Win32_ComputerSystem()[0] # computer system information list 
my_os_system = c.Win32_OperatingSystem()[0] # operating system information list

print(f'Manufacturer: {my_system.Manufacturer}')
print(f'Model: {my_system.Model}')
print(f'Name: {my_system.Name}')
print(f'NumberOfProcessors: {my_system.NumberOfProcessors}')
print(f'SystemType: {my_system.SystemType}')
print(f'SystemFamily: {my_system.SystemFamily}')
print(f'Installed OS: {my_os_system.Caption}')