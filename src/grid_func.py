
import numpy as np
from datetime import datetime
import pickle as pkl

def gen_time_array(intime_var,outrow,outcol):

    dt1 = []
    leng = len(intime_var)

    for i in range(leng):
        t = str(intime_var[i][:15].decode())
        parsed_dt = datetime.strptime(t, "%Y%m%d %H%M%S")
        ref_date = datetime(1997, 1, 1, 0, 0, 0)
        time_diff = (parsed_dt - ref_date).total_seconds()
        dt1.append(time_diff)

##    print(len(dt1))
    desired_time1 = np.repeat(dt1, outcol).reshape(outrow, outcol).astype(float)
    return desired_time1
##    print(desired_time1.shape)

def minmax(lt1, lt2, ln1, ln2):
    mn_lt1 = np.floor(np.min(lt1[(lt1>=-90.0)*(lt1<=90.0)])/10.0)*10.0
    mn_lt2 = np.floor(np.min(lt2[(lt2>=-90.0)*(lt2<=90.0)])/10.0)*10.0
    com_lat_min = max(np.min([mn_lt1, mn_lt2]),-90.0)
    mx_lt1 = np.ceil(np.max(lt1[(lt1>=-90.0)*(lt1<=90.0)])/10.0)*10.0
    mx_lt2 = np.ceil(np.max(lt2[(lt2>=-90.0)*(lt2<=90.0)])/10.0)*10.0
    com_lat_max = min(np.max([mx_lt1, mx_lt2]),90.0)

    mn_ln1 = np.floor(np.min(ln1[(ln1>=-180.0)*(ln1<180.0)])/10.0)*10.0
    mn_ln2 = np.floor(np.min(ln2[(ln2>=-180.0)*(ln2<180.0)])/10.0)*10.0
    com_lon_min = max(np.min([mn_ln1, mn_ln2]),-180.0)
    mx_ln1 = np.ceil(np.max(ln1[(ln1>=-180.0)*(ln1<180.0)])/10.0)*10.0
    mx_ln2 = np.ceil(np.max(ln2[(ln2>=-180.0)*(ln2<180.0)])/10.0)*10.0
    com_lon_max = min(np.max([mx_ln1, mx_ln2]),180.0)
    
    
    return com_lat_min, com_lat_max, com_lon_min, com_lon_max

def grid(lat, lon, keywrds, mnlt, mxlt, mnln, mxln, grdsz, mask, data):
    
    rw=np.shape(lat)[0]
    cl=np.shape(lat)[1]
    lend=len(data)
    szx=np.int32((mxlt-mnlt)/grdsz)
    szy=np.int32((mxln-mnln)/grdsz)
    tij = []

#    print(mnlt, mxlt, mnln, mxln, grdsz,szx,szy,"^^^^^")
    tdct={}; odct={}; val={}; cnt={}
    for ii in data.keys():
        if ii in keywrds:
            continue
        else:
            tdct[ii]=data[ii]
            odct[ii]=np.ones([szx,szy])*-9999.0
            val[ii]=np.zeros([szx,szy])
            cnt[ii]=np.zeros([szx,szy])
       
    try:
        for ii in np.arange(0,rw):
            for jj in np.arange(0,cl,1):
                if ((lat[ii,jj]>40.0)+(lat[ii,jj]<-40.0)):
                    continue
                if ((lon[ii,jj]>180.0)+(lon[ii,jj]<=-180.0)):
                    continue
                if ((lon[ii,jj]>=179.9)*(lon[ii,jj]<=180.0)):
                    continue
                if ((lon[ii,jj]>=-180.0)*(lon[ii,jj]<-179.9)):
                    continue
                i1=np.int32((lat[ii,jj]-mnlt)/grdsz)
                j1=np.int32((mxln+lon[ii,jj])/grdsz)
                tij.append([i1,j1, lat[ii,jj], lon[ii,jj], ii, jj])
                
                for kk in tdct.keys():
                    val[kk][i1,j1]=val[kk][i1,j1]+tdct[kk][ii,jj]
                    cnt[kk][i1,j1]=cnt[kk][i1,j1]+1
#        
        for kk in tdct.keys():
            ar1=val[kk]; ar2=cnt[kk]
            odct[kk][(ar1>0.0)*(ar2>0.0)]=ar1[(ar1>0.0)*(ar2>0.0)]/ar2[(ar1>0.0)*(ar2>0.0)]
        odct['mask']=mask 
        
    except OSError as e:
        print(e)
        
    return odct, tij


def threshold(path, files):
    ll = len(files)
    new_data = []
    new_data1 = []
    new_data10 =[]
#    new_data.append(['i', 'j', 'dcc', 'level', 'solza', 'stza', 'relaa' 'vis', 'tir', 'mask'])
    count = 0
    for ii in range(ll):
        file = path + '/SCR/' + files[ii]
        
        f =  open(file, 'rb')
        data = pkl.load(f)
        f.close()
        
        mask = data['mask'].flatten()
        dcc = data['dcc'].flatten()
        sza = data['solza'].flatten()
        stza = data['stznsc'].flatten()
        rela = data['relaa'].flatten()
        vis = data['fr_visc'].flatten()
        tir = data['fr_insc'].flatten()
        lvl = data['dcc-level'].flatten()
        ltmn = data['ltmin']
        ltmx = data['ltmax']
        lnmn = data['lnmin']
        lnmx = data['lnmax']
        gdsz = data['gridsz']
        i1=data['i'].flatten()
        j1=data['j'].flatten()
        
        param = [ltmn, ltmx, lnmn, lnmx, gdsz]
          
        # dcc_n=dcc[dcc!=-9999.0]
        
        jj = len(dcc)
        cnt = 0
        new10 = []
        new = []
        new1 = []
       
        
        for i in range(jj):
            if dcc[i] != -999.0 and sza[i] != -9999.0 and stza[i] != -9999.0 and rela[i] != -9999.0 and vis[i] != -9999.0 and tir[i] != -9999.0:
            # if dcc[i] == 1:  
                new10.append(i1[i])
                new10.append(j1[i])
                new10.append(dcc[i])
                new10.append(lvl[i])
                new10.append(sza[i])
                new10.append(stza[i])
                new10.append(rela[i])
                new10.append(vis[i])
                new10.append(tir[i])
                new10.append(mask[i])
                
                                
                
                cnt += 1
                new_data10.append(new10)
                del new10
                new10 = []
            if dcc[i] == 1 and sza[i] != -9999.0 and stza[i] != -9999.0 and rela[i] != -9999.0 and vis[i] != -9999.0 and tir[i] != -9999.0:
            # if dcc[i] == 1: 
                new.append(i1[i])
                new.append(j1[i])
                new.append(dcc[i])
                new.append(lvl[i])
                new.append(sza[i])
                new.append(stza[i])
                new.append(rela[i])
                new.append(vis[i])
                new.append(tir[i])
                new.append(mask[i])
                
                cnt += 1
                new_data.append(new)
                del new
                new = []
            # elif dcc[i] == 0:  
            elif dcc[i] == 0 and sza[i] != -9999.0 and stza[i] != -9999.0 and rela[i] != -9999.0 and vis[i] != -9999.0 and tir[i] != -9999.0:
                new1.append(i1[i])
                new1.append(j1[i])
                new1.append(dcc[i])
                new1.append(lvl[i])
                new1.append(sza[i])
                new1.append(stza[i])
                new1.append(rela[i])
                new1.append(vis[i])
                new1.append(tir[i])
                new1.append(mask[i])
                
                cnt += 1
                new_data1.append(new1)
                del new1
                new1 = []
            else:
                continue
        
        count += cnt
    
        print("----done-----", ii)
    
    thr_F1 = path + '/flag1.pkl'
    thr_F2 = path + '/flag0.pkl'
    thr_F3 = path + '/flag10.pkl'
    para = path + 'param.pkl'

    try:
        f1 = open(thr_F1, 'wb')
        pkl.dump(new_data, f1)
        f1.close()
        
        f1 = open(thr_F2, 'wb')
        pkl.dump(new_data1, f1)
        f1.close()
        
        f1 = open(thr_F3, 'wb')
        pkl.dump(new_data10, f1)
        f1.close()
        
        f1 = open(para, 'wb')
        pkl.dump(param, f1)
        f1.close()
    except FileNotFoundError as e:
        print(e)
    

    
    # print(count)
    return new_data, new_data1, new_data10, param


# # pi=3.14
# def dcc_flag(tb1,tb2,tb3,tb4,tb5,stznsp):
    
#     rw=len(tb1)
#     cl=len(tb1[0])
#     flag=np.int16(np.ones(np.shape(tb1))*-999)
#     lvl = np.int16(np.ones(np.shape(tb1))*-999)
#     stz_rad=np.ones(np.shape(tb1))*-99999.0
#     TD=np.ones(np.shape(tb1))*-99999.0
#     # flag=np.zeros(np.shape(tb1))
#     # lvl = np.ones(np.shape(tb1))
#     # stz_rad=np.zeros(np.shape(tb1))
#     # TD=np.zeros(np.shape(tb1))    
            
#     for i in range(rw):
#         for j in range(cl):
#             stz_rad[i][j]=np.float64(np.radians(stznsp[i][j]))
#             TD[i][j]=np.float64(0.04761-(0.01678*stz_rad[i][j])+0.00599*pow(stz_rad[i][j],2))
#             if(tb1[i][j]<=230.0 and tb1[i][j]>=-230.0):
#                 flag[i][j]=np.int16(1)
#                 if({(tb1[i][j]-tb5[i][j])>=TD[i][j]}and{(tb1[i][j]-tb4[i][j])>=TD[i][j]}and{(tb1[i][j]-tb3[i][j])>=TD[i][j]}and{(tb1[i][j]-tb2[i][j])>=TD[i][j]}):
#                     lvl[i][j] = np.int16(11)
#                 elif({(tb2[i][j]-tb5[i][j])>=TD[i][j]}and{(tb2[i][j]-tb4[i][j])>=TD[i][j]}and{(tb2[i][j]-tb3[i][j])>=TD[i][j]}):
#                     lvl[i][j]=np.int16(12)
#                 elif({(tb3[i][j]-tb5[i][j])>=TD[i][j]}and{(tb3[i][j]-tb4[i][j])>=TD[i][j]}):
#                     lvl[i][j]=np.int16(13)
#                 elif((tb4[i][j]-tb5[i][j])>=TD[i][j]):
#                     lvl[i][j]=np.int16(14)
#                 elif(tb1[i][j]<=180.0):
#                     lvl[i][j]=np.int16(15)
#                 else:
#                     lvl[i][j]=np.int16(16)
#             else:
#                 flag[i][j]=np.int16(0)
#                 lvl[i][j]=np.int16(17)
#     return flag,lvl

def dcc_flag(tb1,tb2,tb3,tb4,tb5,stznsp):
    t1= tb1.flatten()
    t2= tb2.flatten()
    t3= tb3.flatten()
    t4= tb4.flatten()
    t5= tb5.flatten()
    zn= stznsp.flatten()
    fl=np.int16(np.ones(np.shape(t1))*-999)
    ll = np.int16(np.ones(np.shape(t1))*-999)
    stz_rad=np.ones(np.shape(t1))*-99999.0
    TD=np.ones(np.shape(t1))*-99999.0

    stz_rad[np.abs(zn)<90.0]=np.float64(np.radians(zn[np.abs(zn)<90.0]))
    # FIX: the condition was '>90.0', which is never true for valid incidence angles (0-52 deg), so TD stayed at -99999
    # and every DCC pixel received level 11. '<90.0' matches the intent (and the commented-out original above).
    TD[np.abs(zn)<90.0]=np.float64(0.04761-(0.01678*stz_rad[np.abs(zn)<90.0])+0.00599*pow(stz_rad[np.abs(zn)<90.0],2))

    #flag[(tb1<230.0)*(tb1>0.0)]=np.int16(1)
    
    for i in range(len(t1)):
        if(t1[i]<=230.0 and t1[i]>= 0.0):
            fl[i]=np.int16(1)
            if((t1[i]-t2[i])>=TD[i] and (t1[i]-t3[i])>=TD[i] and(t1[i]-t4[i])>=TD[i] and (t1[i]-t5[i])>=TD[i]):
                ll[i]=np.int16(11)
            elif((t2[i]-t3[i])>=TD[i] and (t2[i]-t4[i])>=TD[i] and (t2[i]-t5[i])>=TD[i]):
                ll[i]=np.int16(12)
            elif((t3[i]-t4[i])>=TD[i] and (t3[i]-t5[i])>=TD[i]):
                ll[i]=np.int16(13)
            elif((t4[i]-t5[i])>=TD[i]):
                ll[i]=np.int16(14)
            elif(t1[i]<=180.0):
                ll[i]=np.int16(15)
            else:
                ll[i]=np.int16(16)
        elif(t1[i]!= -9999.0):
            fl[i]=np.int16(0)
            ll[i]=np.int16(17)
        else:
            continue
            

    return fl.reshape(np.shape(tb1)),ll.reshape(np.shape(tb1))                













