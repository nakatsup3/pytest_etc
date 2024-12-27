# コマンド入力サンプル

import pyxel

class APP:
  def __init__(self):
      pyxel.init(128, 128, title="pyxel")
      
      self.frame = 0
      self.f_limit = 10
      self.cmd = 0
      
      pyxel.run(self.update, self.draw)
     
  def update(self):
      if pyxel.btn(pyxel.KEY_R):
          self.frame = 0          
          self.cmd = 0
          
      if self.cmd == 0 and pyxel.btn(pyxel.KEY_RIGHT):
          self.cmd += 1
          
      if self.cmd == 1 and pyxel.btn(pyxel.KEY_DOWN):
          self.cmd += 1
          self.frame = 0

      if self.cmd == 2 and pyxel.btn(pyxel.KEY_RIGHT):
          self.cmd += 1 
          self.frame = 0

      if self.cmd == 3 and pyxel.btn(pyxel.KEY_P):
          self.cmd += 1 
          self.frame = 0
          
      if self.cmd != 0:          
          if self.cmd == 4:
              pass
          else:
              self.frame += 1
              if self.frame > self.f_limit:
                  self.frame = 0
                  self.cmd = 0
   
  def draw(self):
      pyxel.cls(0)
      pyxel.text(10, 10, str(self.frame), 7)
      
      if self.cmd == 1:
          pyxel.text(10, 20, "RIGHT!", 7)
          
      if self.cmd == 2:
          pyxel.text(10, 30, "DOWN!!", 7)          

      if self.cmd == 3:
          pyxel.text(10, 40, "RIGHT!!!", 7)                    
          
      if self.cmd == 4:          
          pyxel.text(10, 50, "SYO-RYU-KEN!!!!", pyxel.frame_count % 16)            
      
      
      
APP()