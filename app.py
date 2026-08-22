import json, os, sys, subprocess, webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

AUTHOR='Naščák Martinsaqirmdevx'; AUTHOR_URL='https://github.com/saqirmdevx'
LANGS={'pt':'🇧🇷 Português','en':'🇺🇸 English','es':'🇪🇸 Español','zh':'🇨🇳 中文','sk':'🇸🇰 Slovenčina'}
MADE={'pt':'Programa feito por:','en':'Program made by:','es':'Programa hecho por:','zh':'程序制作人：','sk':'Program vytvoril:'}
T={
'pt':{'title':'TextureSplitter','png':'PNG','json':'JSON','choose_png':'Selecionar PNG...','choose_json':'Selecionar JSON...','size':'Escolha o tamanho do Sprite:','custom':'Personalizado...','settings':'Configurações do JSON','output':'Pasta de saída:','choose_folder':'Selecionar pasta...','cut':'✂  CORTAR IMAGENS','preview':'Pré-visualização','ready':'Pronto.','select_sprite':'Selecione um sprite na pré-visualização.','frame':'Frame','anchor':'Âncora','source':'Tamanho original','sprite_source':'Tamanho no spritesheet','rotated':'Rotacionado','trimmed':'Recortado','open':'Abrir pasta','shortcut':'Criar atalho na área de trabalho','done':'Concluído! {n} imagens salvas.','errpng':'Escolha o arquivo PNG.','errjson':'Escolha o arquivo JSON.','errout':'Escolha a pasta de saída.','custom_title':'Tamanho personalizado','custom_prompt':'Digite o tamanho do sprite (ex.: 64):','invalid':'Digite um número inteiro maior que zero.'},
'en':{'title':'TextureSplitter','png':'PNG','json':'JSON','choose_png':'Select PNG...','choose_json':'Select JSON...','size':'Choose Sprite Size:','custom':'Custom...','settings':'JSON Settings','output':'Output folder:','choose_folder':'Select folder...','cut':'✂  CUT IMAGES','preview':'Preview','ready':'Ready.','select_sprite':'Select a sprite in the preview.','frame':'Frame','anchor':'Anchor','source':'Source size','sprite_source':'Spritesheet size','rotated':'Rotated','trimmed':'Trimmed','open':'Open folder','shortcut':'Create desktop shortcut','done':'Done! {n} images saved.','errpng':'Choose the PNG file.','errjson':'Choose the JSON file.','errout':'Choose the output folder.','custom_title':'Custom size','custom_prompt':'Enter sprite size (e.g. 64):','invalid':'Enter a positive integer.'},
'es':{'title':'TextureSplitter','png':'PNG','json':'JSON','choose_png':'Seleccionar PNG...','choose_json':'Seleccionar JSON...','size':'Elige el tamaño del Sprite:','custom':'Personalizado...','settings':'Configuración del JSON','output':'Carpeta de salida:','choose_folder':'Seleccionar carpeta...','cut':'✂  CORTAR IMÁGENES','preview':'Vista previa','ready':'Listo.','select_sprite':'Selecciona un sprite en la vista previa.','frame':'Frame','anchor':'Anclaje','source':'Tamaño original','sprite_source':'Tamaño en el spritesheet','rotated':'Rotado','trimmed':'Recortado','open':'Abrir carpeta','shortcut':'Crear acceso directo en el escritorio','done':'¡Listo! {n} imágenes guardadas.','errpng':'Elige el archivo PNG.','errjson':'Elige el archivo JSON.','errout':'Elige la carpeta de salida.','custom_title':'Tamaño personalizado','custom_prompt':'Escribe el tamaño del sprite (ej.: 64):','invalid':'Escribe un número entero mayor que cero.'},
'zh':{'title':'TextureSplitter','png':'PNG','json':'JSON','choose_png':'选择 PNG...','choose_json':'选择 JSON...','size':'选择 Sprite 大小：','custom':'自定义...','settings':'JSON 设置','output':'输出文件夹：','choose_folder':'选择文件夹...','cut':'✂  切割图像','preview':'预览','ready':'就绪。','select_sprite':'请在预览中选择一个 Sprite。','frame':'Frame','anchor':'锚点','source':'原始大小','sprite_source':'Spritesheet 大小','rotated':'旋转','trimmed':'裁剪','open':'打开文件夹','shortcut':'创建桌面快捷方式','done':'完成！已保存 {n} 张图片。','errpng':'请选择 PNG 文件。','errjson':'请选择 JSON 文件。','errout':'请选择输出文件夹。','custom_title':'自定义大小','custom_prompt':'输入 Sprite 大小（例如 64）：','invalid':'请输入大于零的整数。'},
'sk':{'title':'TextureSplitter','png':'PNG','json':'JSON','choose_png':'Vybrať PNG...','choose_json':'Vybrať JSON...','size':'Vyberte veľkosť Sprite:','custom':'Vlastná...','settings':'Nastavenia JSON','output':'Výstupný priečinok:','choose_folder':'Vybrať priečinok...','cut':'✂  ROZDELIŤ OBRÁZKY','preview':'Náhľad','ready':'Pripravené.','select_sprite':'Vyberte Sprite v náhľade.','frame':'Frame','anchor':'Kotva','source':'Pôvodná veľkosť','sprite_source':'Veľkosť v spritesheete','rotated':'Otočené','trimmed':'Orezané','open':'Otvoriť priečinok','shortcut':'Vytvoriť skratku na pracovnej ploche','done':'Hotovo! Uložených obrázkov: {n}.','errpng':'Vyberte PNG súbor.','errjson':'Vyberte JSON súbor.','errout':'Vyberte výstupný priečinok.','custom_title':'Vlastná veľkosť','custom_prompt':'Zadajte veľkosť sprite (napr. 64):','invalid':'Zadajte celé číslo väčšie ako nula.'}}

class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.lang='pt'; self.png=None; self.json_path=None; self.out=None; self.data=None; self.sheet=None; self.selected=None; self.size=64; self.thumbs=[]; self.maximized=False
  self.bg='#10151c'; self.panel='#191f28'; self.panel2='#222a35'; self.border='#303a47'; self.text='#e8edf4'; self.muted='#7f8b9a'; self.accent='#70e6b5'
  self.geometry('1180x800'); self.minsize(980,650); self.configure(bg=self.bg); self.build(); self.refresh(); self.make_shortcut()
 def tr(self,k): return T[self.lang][k]
 def build(self):
  top=tk.Frame(self,bg=self.panel,height=50); top.pack(fill='x'); top.pack_propagate(False)
  self.title_lbl=tk.Label(top,bg=self.panel,fg=self.text,font=('Segoe UI',14,'bold')); self.title_lbl.pack(side='left',padx=16)
  self.lang_btn=tk.Button(top,bg=self.panel,fg=self.text,activebackground=self.panel2,relief='flat',bd=0,cursor='hand2',command=self.lang_menu); self.lang_btn.pack(side='right',padx=5)
  for txt,cmd in [('—',self.iconify),('□',self.toggle_max),('×',self.destroy)]: tk.Button(top,text=txt,bg=self.panel,fg=self.muted,activebackground=self.panel2,activeforeground=self.text,relief='flat',bd=0,width=4,command=cmd).pack(side='right')
  body=tk.Frame(self,bg=self.bg); body.pack(fill='both',expand=True,padx=16,pady=14)
  left=tk.Frame(body,bg=self.bg,width=380); left.pack(side='left',fill='y',padx=(0,12)); left.pack_propagate(False)
  right=tk.Frame(body,bg=self.bg); right.pack(side='left',fill='both',expand=True)
  files=tk.Frame(left,bg=self.panel,highlightbackground=self.border,highlightthickness=1); files.pack(fill='x',pady=(0,10))
  self.png_label=self.lab(files); self.png_label.pack(anchor='w',padx=14,pady=(12,4)); self.png_btn=self.btn(files,self.choose_png); self.png_btn.pack(fill='x',padx=14); self.png_var=tk.StringVar(); tk.Label(files,textvariable=self.png_var,bg=self.panel,fg=self.muted,anchor='w',font=('Segoe UI',8)).pack(fill='x',padx=14,pady=4)
  self.json_label=self.lab(files); self.json_label.pack(anchor='w',padx=14,pady=(5,4)); self.json_btn=self.btn(files,self.choose_json); self.json_btn.pack(fill='x',padx=14); self.json_var=tk.StringVar(); tk.Label(files,textvariable=self.json_var,bg=self.panel,fg=self.muted,anchor='w',font=('Segoe UI',8)).pack(fill='x',padx=14,pady=4)
  self.size_label=self.lab(files); self.size_label.pack(anchor='w',padx=14,pady=(5,4)); self.size_var=tk.StringVar(value='64 x 64'); self.combo=ttk.Combobox(files,textvariable=self.size_var,values=('16 x 16','32 x 32','48 x 48','64 x 64','96 x 96','128 x 128','256 x 256','512 x 512'),state='readonly'); self.combo.pack(fill='x',padx=14); self.combo.bind('<<ComboboxSelected>>',self.size_changed); self.custom_btn=self.btn(files,self.custom_size); self.custom_btn.pack(fill='x',padx=14,pady=(5,12))
  setp=tk.Frame(left,bg=self.panel,highlightbackground=self.border,highlightthickness=1); setp.pack(fill='both',expand=True,pady=(0,10)); self.settings_title=self.lab(setp); self.settings_title.pack(anchor='w',padx=14,pady=(12,6)); self.settings=tk.Text(setp,bg=self.panel2,fg=self.text,relief='flat',font=('Consolas',9),wrap='word'); self.settings.pack(fill='both',expand=True,padx=10,pady=(0,10)); self.settings.configure(state='disabled')
  outp=tk.Frame(left,bg=self.panel,highlightbackground=self.border,highlightthickness=1); outp.pack(fill='x'); self.out_label=self.lab(outp); self.out_label.pack(anchor='w',padx=14,pady=(10,4)); self.out_btn=self.btn(outp,self.choose_output); self.out_btn.pack(fill='x',padx=14); self.out_var=tk.StringVar(); tk.Label(outp,textvariable=self.out_var,bg=self.panel,fg=self.muted,anchor='w',font=('Segoe UI',8)).pack(fill='x',padx=14,pady=4); self.cut_btn=tk.Button(outp,bg='#317b61',fg='white',activebackground=self.accent,relief='flat',bd=0,font=('Segoe UI',10,'bold'),cursor='hand2',command=self.cut); self.cut_btn.pack(fill='x',padx=14,pady=8); self.open_btn=self.btn(outp,self.open_output); self.open_btn.pack(side='left',fill='x',expand=True,padx=(14,4),pady=(0,10)); self.short_btn=self.btn(outp,self.make_shortcut); self.short_btn.pack(side='left',fill='x',expand=True,padx=(4,14),pady=(0,10))
  prev=tk.Frame(right,bg=self.panel,highlightbackground=self.border,highlightthickness=1); prev.pack(fill='both',expand=True); self.prev_title=self.lab(prev); self.prev_title.pack(anchor='w',padx=14,pady=(12,2)); self.count=tk.Label(prev,bg=self.panel,fg=self.muted,font=('Segoe UI',8)); self.count.pack(anchor='w',padx=14,pady=(0,6)); self.canvas=tk.Canvas(prev,bg='#0b1016',highlightthickness=0); sb=ttk.Scrollbar(prev,orient='vertical',command=self.canvas.yview); sb.pack(side='right',fill='y',padx=(0,8),pady=8); self.canvas.pack(side='left',fill='both',expand=True,padx=(10,0),pady=8); self.inner=tk.Frame(self.canvas,bg='#0b1016'); self.win=self.canvas.create_window((0,0),window=self.inner,anchor='nw'); self.inner.bind('<Configure>',lambda e:self.canvas.configure(scrollregion=self.canvas.bbox('all'))); self.canvas.bind('<Configure>',lambda e:self.canvas.itemconfigure(self.win,width=e.width))
  self.status=tk.Label(self,bg='#0b1016',fg=self.muted,anchor='w',font=('Segoe UI',8),padx=14); self.status.pack(fill='x',side='bottom')
  credit=tk.Frame(self,bg=self.bg); credit.pack(fill='x',side='bottom',pady=5); tk.Frame(credit,bg=self.bg).pack(side='left',expand=True); self.credit_prefix=tk.Label(credit,bg=self.bg,fg='#566171',font=('Segoe UI',7)); self.credit_prefix.pack(side='left'); self.credit=tk.Label(credit,bg=self.bg,fg='#748297',font=('Segoe UI',7,'underline'),cursor='hand2'); self.credit.pack(side='left'); self.credit.bind('<Button-1>',lambda e:webbrowser.open(AUTHOR_URL)); tk.Frame(credit,bg=self.bg).pack(side='left',expand=True)
 def lab(self,p): return tk.Label(p,bg=self.panel,fg=self.text,font=('Segoe UI',9,'bold'))
 def btn(self,p,cmd): return tk.Button(p,bg=self.panel2,fg=self.text,activebackground=self.border,activeforeground=self.accent,relief='flat',bd=0,cursor='hand2',font=('Segoe UI',9),command=cmd)
 def refresh(self):
  self.title_lbl.config(text='TextureSplitter'); self.lang_btn.config(text='🌐 '+LANGS[self.lang]); self.png_label.config(text='PNG'); self.png_btn.config(text=self.tr('choose_png')); self.json_label.config(text='JSON'); self.json_btn.config(text=self.tr('choose_json')); self.size_label.config(text=self.tr('size')); self.custom_btn.config(text=self.tr('custom')); self.settings_title.config(text=self.tr('settings')); self.out_label.config(text=self.tr('output')); self.out_btn.config(text=self.tr('choose_folder')); self.cut_btn.config(text=self.tr('cut')); self.prev_title.config(text=self.tr('preview')); self.open_btn.config(text=self.tr('open')); self.short_btn.config(text=self.tr('shortcut')); self.credit_prefix.config(text=MADE[self.lang]+' '); self.credit.config(text=AUTHOR); self.status.config(text=self.tr('ready')); self.update_settings()
 def lang_menu(self):
  m=tk.Menu(self,tearoff=0,bg=self.panel2,fg=self.text,activebackground='#317b61');
  for k,v in LANGS.items(): m.add_command(label=v,command=lambda x=k:self.set_lang(x))
  m.tk_popup(self.lang_btn.winfo_rootx(),self.lang_btn.winfo_rooty()+35)
 def set_lang(self,x): self.lang=x; self.refresh()
 def choose_png(self):
  p=filedialog.askopenfilename(filetypes=[('PNG','*.png'),('All files','*.*')]);
  if p: self.png=Path(p); self.png_var.set(str(self.png)); self.load()
 def choose_json(self):
  p=filedialog.askopenfilename(filetypes=[('JSON','*.json'),('All files','*.*')]);
  if p: self.json_path=Path(p); self.json_var.set(str(self.json_path)); self.load()
 def choose_output(self):
  p=filedialog.askdirectory();
  if p: self.out=Path(p); self.out_var.set(str(self.out))
 def size_changed(self,e=None): self.size=int(self.size_var.get().split('x')[0]) ; self.update_settings()
 def custom_size(self):
  d=tk.Toplevel(self); d.title(self.tr('custom_title')); d.configure(bg=self.panel); d.resizable(False,False); tk.Label(d,text=self.tr('custom_prompt'),bg=self.panel,fg=self.text).pack(padx=18,pady=12); e=tk.Entry(d,bg=self.panel2,fg=self.text,relief='flat'); e.insert(0,str(self.size)); e.pack(padx=18); e.focus_set()
  def ok():
   try:n=int(e.get()); assert n>0
   except: messagebox.showerror('Error',self.tr('invalid'),parent=d); return
   self.size=n; self.size_var.set(f'{n} x {n}'); d.destroy(); self.update_settings()
  tk.Button(d,text='OK',command=ok,bg='#317b61',fg='white',relief='flat',bd=0,padx=20).pack(pady=12); d.bind('<Return>',lambda e:ok())
 def load(self):
  if not self.json_path:return
  try:
   self.data=json.loads(self.json_path.read_text(encoding='utf-8-sig')); self.sheet=Image.open(self.png or (self.json_path.parent/self.data['meta']['image'])).convert('RGBA'); self.render()
  except Exception as e: messagebox.showerror('Error',str(e),parent=self)
 def render(self):
  for w in self.inner.winfo_children():w.destroy()
  self.thumbs=[]; frames=self.data.get('frames',{}); self.count.config(text=f'{len(frames)} sprites');
  for i,(key,fd) in enumerate(frames.items()):
   r,c=divmod(i,5); card=tk.Frame(self.inner,bg=self.panel,highlightbackground=self.border,highlightthickness=1); card.grid(row=r,column=c,padx=5,pady=5,sticky='n'); f=fd['frame']; im=self.sheet.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h'])); scale=min(110/max(im.width,im.height),1); im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.Resampling.NEAREST); bg=Image.new('RGBA',(116,116),(38,45,56,255)); bg.alpha_composite(im,((116-im.width)//2,(116-im.height)//2)); tkim=ImageTk.PhotoImage(bg); self.thumbs.append(tkim); tk.Button(card,image=tkim,bg=self.panel,activebackground=self.panel,relief='flat',bd=0,command=lambda k=key:self.select(k)).pack(padx=4,pady=4); tk.Label(card,text=Path(key).name,bg=self.panel,fg=self.text,font=('Segoe UI',7),wraplength=110).pack(pady=(0,4))
  self.selected=next(iter(frames),None); self.update_settings()
 def select(self,k): self.selected=k; self.update_settings()
 def update_settings(self):
  self.settings.configure(state='normal'); self.settings.delete('1.0','end')
  if not self.data or not self.selected:self.settings.insert('end',self.tr('select_sprite'))
  else:
   f=self.data['frames'][self.selected]; fr=f.get('frame',{}); a=f.get('anchor',{}); ss=f.get('spriteSourceSize',{}); src=f.get('sourceSize',{}); lines=[f'Sprite: {self.selected}','',f'{self.tr("source")}: {fr.get("w","?")} × {fr.get("h","?")}',f'{self.tr("frame")}: x={fr.get("x","?")}, y={fr.get("y","?")}, w={fr.get("w","?")}, h={fr.get("h","?")}',f'{self.tr("anchor")}: X={a.get("x","—")}, Y={a.get("y","—")}',f'{self.tr("sprite_source")}: x={ss.get("x","?")}, y={ss.get("y","?")}, w={ss.get("w","?")}, h={ss.get("h","?")}',f'{self.tr("source")}: {src.get("w","?")} × {src.get("h","?")}',f'{self.tr("rotated")}: {f.get("rotated",False)}',f'{self.tr("trimmed")}: {f.get("trimmed",False)}','',f'Sprite output: {self.size} × {self.size}']; self.settings.insert('end','\n'.join(lines))
  self.settings.configure(state='disabled')
 def targets(self):
  frames=self.data['frames']; anim=self.data.get('animations'); out={}
  if anim:
   for folder,keys in anim.items():
    for key in keys:
     if key in frames: out[key]=Path(folder)/Path(key).name
  else:
   for key in frames: out[key]=Path(key.replace('/','_').replace('\\','_'))
  return out
 def cut(self):
  if not self.png: return messagebox.showwarning('Aviso',self.tr('errpng'))
  if not self.data: return messagebox.showwarning('Aviso',self.tr('errjson'))
  if not self.out: return messagebox.showwarning('Aviso',self.tr('errout'))
  self.out.mkdir(parents=True,exist_ok=True); icc=self.sheet.info.get('icc_profile'); dpi=self.sheet.info.get('dpi'); n=0
  for key,rel in self.targets().items():
   f=self.data['frames'][key]['frame']; im=self.sheet.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']))
   if im.width<=self.size and im.height<=self.size:
    canvas=Image.new('RGBA',(self.size,self.size),(0,0,0,0)); canvas.paste(im,((self.size-im.width)//2,(self.size-im.height)//2)); im=canvas
   path=self.out/rel; path.parent.mkdir(parents=True,exist_ok=True); kw={};
   if icc:kw['icc_profile']=icc
   if dpi:kw['dpi']=dpi
   im.save(path,**kw); n+=1
  self.status.config(text=self.tr('done').format(n=n)); messagebox.showinfo('TextureSplitter',self.tr('done').format(n=n))
 def open_output(self):
  if not self.out:return
  self.out.mkdir(parents=True,exist_ok=True)
  if os.name=='nt':os.startfile(self.out)
  elif sys.platform=='darwin':subprocess.Popen(['open',str(self.out)])
  else:subprocess.Popen(['xdg-open',str(self.out)])
 def toggle_max(self):
  self.maximized=not self.maximized; self.state('zoomed' if self.maximized else 'normal')
 def make_shortcut(self):
  if os.name!='nt':return
  try:
   desktop=Path(os.environ.get('USERPROFILE',str(Path.home())))/'Desktop'; desktop.mkdir(exist_ok=True); link=desktop/'TextureSplitter.lnk'; app=Path(__file__).resolve(); py=Path(sys.executable).with_name('pythonw.exe'); py=py if py.exists() else Path(sys.executable)
   ps=f'''$ws=New-Object -ComObject WScript.Shell;$s=$ws.CreateShortcut('{link}');$s.TargetPath='{py}';$s.Arguments='"{app}"';$s.WorkingDirectory='{app.parent}';$s.Description='TextureSplitter';$s.Save()'''; subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',ps],creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  except Exception:pass

if __name__=='__main__': App().mainloop()
