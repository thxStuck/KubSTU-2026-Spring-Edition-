# [network] The skeleton key

> **Category:** `network`  
> **CTF:** KubSTU CTF 2026 Spring

---

                   

Message: "Listen, we've got some kind of chaos on one of the switches. Errors keep popping up on the ports, logs are flooded, but because of some configuration lock, I can't get through the access levels to figure out which interface is malfunctioning.

  

Take a look at what's going on — I don't just need a report, I need a solution so the network stops throwing warnings. And don't even think about wiping the config!"

 

[3 in 1 .pkt](./files/3 in 1 .pkt)

                  

**Writeup**

  

1. Find the problematic CORE SWITCH. 

  

 ![img_1.png](./images/img_1.png)

                                                  

  

2. In the banner, the player gets a Base64-encoded password for accessing the switch settings. 

3. After entering enable, the player will be prompted for the password they just obtained.

4. After running Show interfaces, they need to find the flag in the description among the ports.


 ![img_2.png](./images/img_2.png)

  

   

  

 

     

     