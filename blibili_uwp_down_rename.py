
# coding: utf-8

# ### B站下载的剧集重命名为正确的命名

# In[ ]:


import json
import os


# In[ ]:


# 剧集数
episode_num = 110

# 剧集文件夹名
episode_folder = "798138961"

for i in range(episode_num):
    with open( episode_folder+"/"+str(i+1)+"/"+episode_folder+".info", "r", encoding="utf-8" ) as load_f:
        load_episode_info = json.load(load_f)
        #print(load_episode_info["PartName"])
        
        episode_name = episode_folder+"/"+str(i+1)+"/"+episode_folder+"_"+str(i+1)+"_0.mp4"
        re_episode_name = episode_folder+"/"+str(i+1)+"/"+load_episode_info["PartNo"]+"_"+load_episode_info["PartName"]+".mp4"
        
        try:
            os.rename(episode_name, re_episode_name)
            
            #print("第"+load_episode_info["PartNo"]+"集，重命名成功")
        except Exception as e:
            print(e)
            print("rename file fail\n"+episode_name+"\n")
        

