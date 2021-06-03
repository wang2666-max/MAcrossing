#!/usr/bin/env python
# coding: utf-8

# In[1]:


# homework3 (Jason Wang jw6542)
# Strategy explained: I will use a simple moving average, with sma20 for short term, sma 100 for long
# to conduct a trading strategy with threshold of 0, so we buy at close when sma20 goes above sma100,
# sell at close when sma20 goes below sma100.
import pandas as pd
import numpy as np
import my_mod as mod
import matplotlib.pyplot as plt
import math
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


# download and load amzn 5 yrs as pd df
df=mod.loadpd('AMZN5')
df.head()


# In[3]:


df=df[['Date','Adj Close']]
df.index=df['Date']
df=df[['Adj Close']]
df.rename(columns={'Adj Close':'close'},inplace=True)
df.head()


# In[4]:


# derive trading days daily return
dflog=pd.DataFrame()
dflog['r']=df['close']/df['close'].shift(1)
dflog.head()


# In[5]:


df['close'].count


# In[6]:


# with random walk, assuming r_t = eps_t, straight bootstrap historical returns.

def bootstrap(i):
    bootstrap=dflog.copy()
    bootstrap=bootstrap.dropna() 
    bootstrap['boot']=np.random.randint(1321, size=1321)
    bootstrap['bootstrap']=[0]*1321
    for b in range(1321):
        num=bootstrap['boot'].iloc[b]
        bootstrap['bootstrap'].iloc[b]=bootstrap['r'].iloc[num]
#     print(bootstrap[:5])
    bootstrap.drop(columns=['r','boot'],inplace=True)
    return bootstrap
test=bootstrap(0)


# In[7]:


#     print(bootstrap[:5])


# In[8]:


# check to see if the bootstrapped return looks normal
test.head(20)


# In[9]:


dflog.head()


# In[10]:


# check if these two means are similar
dflog['r'].mean()


# In[11]:


test['bootstrap'].mean()


# In[12]:


# conduct price with bootstrapped r
pricearray=[]
pricearray.append(df)
# append df as the first element, the true historical price
def bootprice(i):
    bootp=df.copy()
    for p in range (1,len(df)):
        bootp['close'].iloc[p]=bootp['close'].iloc[p-1]*(bootreturn['bootstrap'].iloc[p-1])
    pricearray.append(bootp)


# In[13]:


# price array append 100 simulations
for times in range(100):
    bootreturn=pd.DataFrame()
    bootreturn=bootstrap(times)
    bootprice(times)


# In[14]:


pricearray[0].head()


# In[15]:


# check to see if the last bootreturn matches the last simulated price
bootreturn.head()


# In[16]:


pricearray[100].head()


# In[17]:


pricearray[37].tail()


# In[18]:


len(pricearray)


# In[19]:


# with an array of dataframe, write a for loop for ma
maarray=[]
for i in range(101):
    result=pricearray[i]
    result.columns=['p']
    result['20']=result['p'].rolling(window=20).mean()
    result['100']=result['p'].rolling(window=100).mean()
    result=result.dropna()
    maarray.append(result)
maarray[100].head()


# In[20]:


tradearray=[]
for i in range(101):
    

    target=maarray[i]
    buying=[]
    selling=[]
    buyingdates=[]
    sellingdates=[]

#recording buy sell price and dates
#     flag=1 when sma20>sma100, and flag=0 when sma20<sma100
    if  target['20'].iloc[0]<=target['100'].iloc[0]:
        flag=0
    else:
        flag=1

    for z in range(len(target)):
        if (target['20'].iloc[z]<target['100'].iloc[z] and flag==1):
            selling.append(target['p'].iloc[z])
            sellingdates.append(z)
            flag=0
        
        if (target['20'].iloc[z]>target['100'].iloc[z] and flag==0):
            buying.append(target['p'].iloc[z])
            buyingdates.append(z)
            flag=1
# first order has to be buy
    if(sellingdates[0]<buyingdates[0]):
        selling.pop(0)
        sellingdates.pop(0)

# round trip check
    if(len(sellingdates)>len(buyingdates)):
        selling.pop(len(sellingdates)-1)
        sellingdates.pop(len(sellingdates)-1)
    if(len(sellingdates)<len(buyingdates)):
        buying.pop(len(buyingdates)-1)
        buyingdates.pop(len(buyingdates)-1)
#into a dataframe    
    trades=pd.DataFrame()
    trades['buying']=buying
    trades['buyingdates']=buyingdates
    trades['selling']=selling
    trades['sellingdates']=sellingdates

    trades['log return']=(trades['selling']/trades['buying'])
    trades['log return']=[math.log(x) for x in trades['log return']]
    trades['daily log return']=trades['log return']/(trades['sellingdates']-trades['buyingdates'])
    def win(x):
        if trades.iloc[x,0]<trades.iloc[x,2]:
            return 1
        else:
            return 0

    winning=[]
    for x in range(len(trades)):
        winning.append(win(x))
    trades['winning trades']=winning
    tradearray.append(trades)
tradearray[100]


# In[21]:


sumarray=[]
for i in range(101):
    summary=pd.Series(dtype='float64')
    t=tradearray[i]
    p=pricearray[i]
    summary['Sample']='B'+str(i)
    summary['number of round trips']=len(t)
    summary['total return per year']=t['log return'].sum()/5
    summary['buy and hold return per year']=math.log(p['p'].iloc[len(p)-1]/p['p'].iloc[0])/5
    summary['win percent']=t['winning trades'].sum()/len(trades)
    summary['max drawdown']=t['log return'].min()
    summary['sharpe ratio']=t['log return'].mean()/t['log return'].std()
    sumarray.append(summary)
sumarray[100]


# In[28]:


tosum= pd.DataFrame( columns = ['Sample','number of round trips','total return per year','buy and hold return per year','win percent','max drawdown','sharpe ratio'])
for i in range(101):
    tosum.loc[i] = sumarray[i]
tosum['Sample'].iloc[0]='Historical'
tosum.head()


# In[23]:


tosum.tail(10)


# In[24]:


tosum['total return per year'].mean()


# In[43]:


finalmean=pd.DataFrame(data=np.zeros(shape=(1,6)), columns = ['number of round trips','total return per year','buy and hold return per year','win percent','max drawdown','sharpe ratio'])
for strings in (finalmean.columns):
    finalmean[strings]=tosum[strings].mean()
finalmean


# In[44]:


plt.title('return per year')
plt.ylabel('count')
plt.hist(tosum['total return per year'], edgecolor='black')
plt.show()


# In[ ]:




