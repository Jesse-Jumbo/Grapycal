from grapycal import Node, TextControl, ListTopic, ObjDictTopic
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort, OutputPort
from .math import *

class LambdaNode(Node):
    category = 'function'
    def build_node(self):
        self.label.set('Lambda')
        self.shape.set('normal')
        self.text_controls = self.add_attribute('text_controls',ObjDictTopic[TextControl])

        self.input_args = self.add_attribute('input_args',ListTopic,editor_type='list')
        self.outputs = self.add_attribute('outputs',ListTopic,editor_type='list')

    def init_node(self):
        self.input_args.on_insert.add_auto(self.on_input_arg_added)
        self.input_args.on_pop.add_auto(self.on_input_arg_removed)

        if self.is_new:
            self.input_args.insert('x')

        self.outputs.add_validator(ListTopic.unique_validator)
        self.outputs.on_insert.add_auto(self.on_output_added)
        self.outputs.on_pop.add_auto(self.on_output_removed)

        if self.is_new:
            self.outputs.insert('')
            self.text_controls[''].text.set('x')

    def recover_from_version(self, version, old: NodeInfo):
        super().recover_from_version(version, old)
        self.input_args.set(old['input_args'])
        self.outputs.set(old['outputs'])
        for out_name in old['outputs']:
            self.text_controls[out_name].text.set(old.controls[out_name]['text'])
    
    def on_input_arg_added(self, arg_name, position):# currently only support adding to the end
        self.add_in_port(arg_name,1,display_name = arg_name)

    def on_input_arg_removed(self, arg_name, position):
        self.remove_in_port(arg_name)

    def on_output_added(self, name, position):
        self.add_out_port(name,display_name = name)
        new_control = self.add_control(TextControl,name=name)
        self.text_controls[name]=new_control
        new_control.label.set(f'{name}= ')
        
    def on_output_removed(self, name, position):
        self.remove_out_port(name)
        self.text_controls.pop(name)
        self.remove_control(name)

    def input_edge_added(self, edge: Edge, port: InputPort):
        self.calculate()

    def edge_activated(self, edge: Edge, port: InputPort):
        self.calculate()

    def calculate(self):
        for port in self.in_ports:
            if not port.is_all_edge_ready():
                return
            if len(port.edges) == 0:
                return
        arg_values = [port.get_one_data() for port in self.in_ports]

        def task():
            for out_name, text_control in self.text_controls.get().items():
                expr = f'lambda {",".join(self.input_args)}: {text_control.text.get()}'
                y = eval(expr,self.workspace.vars())(*arg_values)
                self.get_out_port(out_name).push_data(y)
                
        self.run(task)