# 右家智能家居组件 For Home Assistant

Author: Vincent Qiu nov30th[AT)gmail.com

## Features

Manages connections to Laite(莱特) Device automatically, the interfaces for each component are packed friendly.  
Easily by using **Send** and **Recv events** with this component to Laite devices.

## Full Configuration

### configuration.yaml Example

    youjia:
      - platform: host
        name: main
        host: 192.168.1.200
        port: 4196
        device_id: 1811102E
        contorl_delay: 0.3
      - platform: switch
        entity_id: '1ACA1008B4'
        name: 'Testing X160'
        device_name: 'Testing X160'
        host_name: main
        auto: true
        names:
          0: "演示"
          1: "客厅"
          2: "厨房"
          3: "123"
          4: '123'
          5: '3333'
          100: "1-9按钮"
          101: "10-18按钮"
          102: "全部按钮"
    
      - platform: switch
        entity_id: '1ACA1008B4'
        name: 'Testing X160'
        device_name: 'Testing X160'
        host_name: main
        auto: false
        names:
          9: "同样的继电器其他按钮"
          

**host** should be the first in platforms, put all the host sections before any other platforms under **youjia**.

Other platforms under **youjia** must have the **host_name** value which points to the one host above.

E.g. If you have two Laite network host and switch A is connected to Laite network host B, the switch A must be put host_name as Laite network host B's name. The value in this example is **"main"**.

### Value required


\- platform: host **(Required)**  
> name: main **(Required**, used for other youjia platform communication)  
host: 192.168.1.200 **(Required**, Laite host IP address)  
port: 4196 **(Required**, Laite host port)  
device_id: 1811102E **(Required**, Laite device ID, 8 chars)  
contorl_delay: 0.3 **(Required**, interval between all commands to this host, unit: second)  


## X160 Swtich Configuration

X160 has 18 roads control, also including 1-9 roads all on/off and 10-18 roads all on/off control.
Configuration can be multiple sections with one switch, please notice that if you have two same X160 devices, set the auto as true on one device only.


\- platform: switch **(Required)**  
> entity_id: '1ACA1008B4' **(Required**, Laite switch device ID)  
name: 'Testing X160' **(Required**, given name by you)  
device_name: 'Testing X160' **(Required**, given name by you)  
host_name: main **(Required**, the field should be same as one host name in your configuration)  
auto: true **(Required**, if true, a thread will be created to fetch the switch button status each 20 secs)  
names:  **(Required)**  
>>  0: "演示"  
  1: "客厅"  
  2: "厨房"  
  3: "123"  
  4: '123'  
  5: '3333'  
  100: "1-9按钮"  **(Optional**, ID 100 will control the 1-9 roads on switch)  
  101: "10-18按钮" **(Optional**, ID 101 will control the 10-18 roads on switch)  
  102: "全部按钮" **(Optional**, ID 100 will control the all roads on switch)  

**Latest Updated: 20190707**
