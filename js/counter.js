self.addEventListener('message', function(e) {
  let bigarr=e.data[0];
  let sum=0;
  let newarr=[];
  for (let i = 0; i < bigarr.length; i++) {
    sum=sum+bigarr[i];
  }
  let aver=sum/bigarr.length;
  for (let i = 0; i < bigarr.length; i++) {
      if(bigarr[i]>=aver){
          newarr.push(i);
      }
  } 
  self.postMessage(newarr);
}, false);
