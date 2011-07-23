import numpy as np
from dipy.sims.voxel import SingleTensor
from dipy.core.geometry import vec2vec_rotmat
from dipy.data import get_data    
from dipy.viz import fvtk
from dipy.reconst.dti import Tensor

def diff2eigenvectors(dx,dy,dz):
    """ numerical derivatives 2 eigenvectors 
    """
    basis=np.eye(3)
    u=np.array([dx,dy,dz])
    u=u/np.linalg.norm(u)
    R=vec2vec_rotmat(basis[:,0],u)
    eig0=u
    eig1=np.dot(R,basis[:,1])
    eig2=np.dot(R,basis[:,2])
    eigs=np.zeros((3,3))
    eigs[:,0]=eig0
    eigs[:,1]=eig1
    eigs[:,2]=eig2    
    return eigs, R


def orbitual_phantom(bvals=None,
                     bvecs=None,
                     evals=np.array([1.4,.35,.35])*10**(-3),
                     func=None,
                     t=np.linspace(0,2*np.pi,1000),
                     volshape=(64,64,64,65),
                     origin=(32,32,32),
                     scale=(25,25,25),
                     angles=np.linspace(0,2*np.pi,32),
                     radius=np.linspace(0.2,2,6),
                     S0=100.,
                     snr=200.):
    """ Create a phantom based on a 3d orbit f(t)->(x,y,z)
    
    Parameters
    -----------
    bvals : 
    bvecs :
    evals : 
    func : user defined function f(t) 
        if None creates a circular orbit
    
    Returns
    ---------
    
    """
    
    if bvals==None:
        fimg,fbvals,fbvecs=get_data('small_64D')    
        bvals=np.load(fbvals)
        bvecs=np.load(fbvecs)
        bvecs[np.isnan(bvecs)]=0
        
    if func==None:
        x=np.sin(t)
        y=np.cos(t)
        z=np.zeros(t.shape)
    else:
        x,y,z=func(t)
        
    #stop 
    
    dx=np.diff(x)
    dy=np.diff(y)
    dz=np.diff(z)
    
    x=scale[0]*x+origin[0]
    y=scale[1]*y+origin[1]
    z=scale[2]*z+origin[2]
        
    bx=np.zeros(len(angles))
    by=np.sin(angles)
    bz=np.cos(angles)
    
    vol=np.zeros(volshape)    
    sigma=np.float(S0)/np.float(snr)
    
    #stop
    
    for i in range(len(dx)):
        evecs,R=diff2eigenvectors(dx[i],dy[i],dz[i])        
        S=SingleTensor(bvals,bvecs,S0,evals,evecs,snr=None)
        #print sigma, S0/snr, S0, snr
        noise=np.random.normal(0,sigma)
        #add racian noise
        S=np.sqrt((S+noise)**2+noise**2)        
        vol[x[i],y[i],z[i],:]+=S
        for r in radius:
            for j in range(len(angles)):
                rb=np.dot(R,np.array([bx[j],by[j],bz[j]])) 
                vol[x[i]+r*rb[0],y[i]+r*rb[1],z[i]+r*rb[2]]+=S
    
    ten=Tensor(vol,bvals,bvecs)
    FA=ten.fa()
    FA[np.isnan(FA)]=0

    return FA
        

if __name__ == "__main__":
    
    def f(t):
        x=np.sin(t)
        y=np.cos(t)
        #z=np.zeros(t.shape)
        z=np.linspace(-1,1,len(x))
        return x,y,z
    
    FA=orbitual_phantom(func=f)

    