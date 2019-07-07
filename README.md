# 右家智能家居组件 For Home Assistant


## Features

Manages connections to Laite(莱特) Device automatically, the interfaces for each components are packed friendlly.  
Easily by using **Send** and **Recv events** with this components to Laite devices.

## Configuration

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
        names:
          0: "演示"
          1: "客厅"
          2: "厨房"
          3: "123"
          4: '123'
          5: '3333'
    
      - platform: switch
        entity_id: '1ACA1008B4'
        name: 'Testing X160'
        device_name: 'Testing X160'
        host_name: main
        names:
          0: "假的第二个继电器"

**host** should be the first in platforms, put all the host sections before any other platforms under **youjia**.

Other platforms under **youjia** must have the **host_name** value which point to the one host above.

E.g. If you have two Laite neteork host and switch A is connected to Laite network host B, the switch A must be put host_name as Laite network host B's name. The value in this example is **"main"**.

### Value required


\- platform: host **(Required)**  
> name: main **(Required**, used for other youjia platform communication)  
host: 192.168.1.200 **(Required**, Laite host IP address)  
port: 4196 **(Required**, Laite host port)  
device_id: 1811102E **(Required**, Laite device ID, 8 chars)  
contorl_delay: 0.3 **(Required**, interval between all commands to this host, unit: second)  





**Latest Updated: 20190707**
