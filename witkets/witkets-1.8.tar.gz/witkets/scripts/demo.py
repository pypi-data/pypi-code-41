#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
import witkets as wtk

default_theme_gui = '''
<root>
  <button wid='btn-previous' text='Previous' />
  <button wid='btn-next' text='Next' />
  <cardlayout wid='card-widgets'>
	<frame wid='labels'>
		<label wid='h1-labels' text='Labels' style='Header.TLabel' />
		<label wid='lbl1' text='Normal' />
		<label wid='lbl2' text='Error (Error.TLabel)' style='Error.TLabel' />
		<label wid='lbl3' text='OK (Success.TLabel)' style='Success.TLabel' />
		<label wid='lbl4' text='Title (Header.TLabel)' style='Header.TLabel' />
		<geometry>
			<pack for='h1-labels' />
			<pack for='lbl1' />
			<pack for='lbl2' />
			<pack for='lbl3' />
			<pack for='lbl4' />
		</geometry>
	</frame>
	<frame wid='entries'>
		<label wid='h1-entries' text='Entries' style='Header.TLabel' />
		<entry wid='entry1' />
		<entry wid='entry2' />
		<entry wid='entry3' />
		<entry wid='entry4' style='Invalid.TEntry' />
		<entry wid='entry5' style='Incomplete.TEntry' />
		<geometry>
			<pack for='h1-entries' />
			<pack for='entry1' pady='10' />
			<pack for='entry2' pady='10' />
			<pack for='entry3' pady='10' />
			<pack for='entry4' pady='10' />
			<pack for='entry5' pady='10' />
		</geometry>
	</frame>
	<frame wid='buttons'>
		<label wid='h1-buttons' text='Buttons' style='Header.TLabel' />
		<button wid='btn1' text='Normal' />
		<button wid='btn2' text='Disabled Button' state='disabled' />
		<button wid='btn3' text='Primary Button' style='Primary.TButton' />
		<button wid='btn4' text='Primary Disabled' state='disabled' style='Primary.TButton' />
		<button wid='btn5' text='Cancel Button' style='Cancel.TButton' />
		<geometry>
			<pack for='h1-buttons' />
			<pack for='btn1' pady='10' />
			<pack for='btn2' pady='10' />
			<pack for='btn3' pady='10' />
			<pack for='btn4' pady='10' />
			<pack for='btn5' pady='10' />
		</geometry>
	</frame>
	<frame wid='frames'>
		<label wid='h1-frames' text='Frames' style='Header.TLabel' />
		<frame wid='frm1' style='Bordered.TFrame'>
			<label wid='frm1-lbl1' text="Bordered.TFrame" />
			<geometry>
				<pack for='frm1-lbl1' pady='10' padx='10' />
			</geometry>
		</frame>
		<themedlabelframe wid='frm2' title='witkets.ThemedLabelFrame'>
		<label wid='frm2-lbl1' 
			   text="ThemedLabelFrame allows styling Label and Frame" />
			<geometry>
				<pack for='frm2-lbl1' pady='10' padx='10' />
			</geometry>
		</themedlabelframe>
		<geometry>
			<pack for='h1-frames' />
			<pack for='frm1' padx='10' pady='10' />
			<pack for='frm2' padx='10' pady='10' />
		</geometry>
	</frame>
	<frame wid='misc'>
		<label wid='lbl-spinbox' text='Spinbox: ' />
		<spinbox wid='spinbox' from='10' to='20'>
			<wtk-textvariable name='spinbox' value='15' type='int' />
		</spinbox>
		<geometry>
			<grid for='lbl-spinbox' row='0' column='0' sticky='e' />
			<grid for='spinbox' row='0' column='1' sticky='w' />
		</geometry>
	</frame>
  	<geometry>
  		<card for='labels' name='labels' />
  		<card for='entries' name='entries' />
  		<card for='buttons' name='buttons' />
  		<card for='frames' name='frames' />
		<card for='misc' name='misc' />
  	</geometry>
  </cardlayout>
  <geometry>
  	<pack for='btn-previous' side='left' anchor='n' padx='10' />
  	<pack for='btn-next' side='right' anchor='n' padx='10' />
  	<pack for='card-widgets' side='top' anchor='n' padx='10' pady='10' />
  </geometry>
</root>'''

root = tk.Tk()
root.title('Witkets Demo')
builder = wtk.TkBuilder(root)
builder.build_from_string(default_theme_gui)
s = wtk.Style()
s.theme_use('clam')
s.set_default_fonts()
s.apply_default()
cardlayout = builder.nodes['card-widgets']
builder.nodes['btn-next']['command'] = lambda x=cardlayout: x.next()
builder.nodes['btn-previous']['command'] = lambda x=cardlayout: x.previous()
builder.nodes['entry1'].insert(0, 'Test')
builder.nodes['entry2'].insert(0, 'Disabled')
builder.nodes['entry3'].insert(0, 'Read Only')
builder.nodes['entry4'].insert(0, 'Invalid.TEntry')
builder.nodes['entry5'].insert(0, 'Incomplete.TEntry')
builder.nodes['entry2']['state'] = 'disabled'
builder.nodes['entry3']['state'] = 'readonly'
#builder.nodes['entry4']['state'] = 'disabled'
#builder.nodes['entry5']['state'] = 'readonly'
root.mainloop()