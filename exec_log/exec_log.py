import gtk
import csv
import gobject
from datetime import datetime, timedelta
import time

class ExecLog:

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.useropts = useropts

        #init counters
        self.filtered_rows = 0
        self.filtered_duration = 0

        #fill combobox
        self.filter_date_store = gtk.ListStore(int, str)
        self.filter_date_store.append([99999999, "All"])
        self.filter_date_store.append([86400, "Day"])
        self.filter_date_store.append([604800, "Week"])
        self.filter_date_store.append([2419200, "Month"])
        self.filter_date_store.append([29030400, "Year"])

        self.filter_date = builder.get_object("combobox1")
        self.filter_date.set_model(self.filter_date_store)
        self.filter_date.connect("changed", self.on_filter_date_combo_changed)
        self.renderer_text = gtk.CellRendererText()
        self.filter_date.pack_start(self.renderer_text, True)
        self.filter_date.add_attribute(self.renderer_text, "text", 1)
        self.date_filter_value = 0
        #load our database
        self.parents_list = []
        self.model = gtk.TreeStore(str, int, str, int, str, int, str, bool)

        self.parent_iter = self.model.get_iter_first()
        # create Parent TreeView
        self.tv = builder.get_object("tvParent")
        self.renderer = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn("Title", self.renderer, text=0)
        self.tv.append_column(self.column)
        # Create child TreeView
        self.tvChild = builder.get_object("tvChild")
        self.colStartTime = gtk.TreeViewColumn("Start Time", self.renderer, text=2)
        self.colEndTime = gtk.TreeViewColumn("End Time", self.renderer, text=4)
        self.colDuration = gtk.TreeViewColumn("Duration", self.renderer, text=6)
        self.tvChild.append_column(self.colStartTime)
        self.tvChild.append_column(self.colEndTime)
        self.tvChild.append_column(self.colDuration)
        #create date filter
        self.date_filter = self.model.filter_new()
        self.date_filter.set_visible_func(self.date_filter_func)
        self.tv.set_model(self.date_filter)
        # create a filter model for the second view
        self.childFilter = self.model.filter_new()
        self.childFilter.set_visible_func(self.child_filter_func)
        self.tvChild.set_model(self.childFilter)
        #connect text input
        self.filterText = builder.get_object("entry1")
        #connect button
        self.applyBtn = builder.get_object("button1")
        self.applyBtn.connect("released", self.on_applybtn_release)
        #connect reread button
        self.reloadBtn = builder.get_object("button2")
        self.reloadBtn.connect("clicked", self.load_data)
        #connect status bar
        self.statusbar = builder.get_object("statusbar1")

    #load csv data to a model
    def load_data(self, btn):
        print("start_load_data")
        self.parents_list = []
        rows = 0
        unique = 0
        with open('./exec_log/test.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                parent_index = self.contains(row[0], self.parents_list)
                #first occurence
                if  parent_index == -1:
                    self.parents_list.append([row[0]])
                    parent_index = len(self.parents_list) - 1
                    unique = unique + 1
                #convert unixtime to hooman readable format
                start_time = datetime.utcfromtimestamp(int(row[1])).strftime('%d.%m.%Y %H:%M:%S')
                end_time = datetime.utcfromtimestamp(int(row[2])).strftime('%d.%m.%Y %H:%M:%S')
                duration = sec = timedelta(seconds=((int(row[2]) - int(row[1]))))
                # self.parents_list[parent_index].append([row[0], (row[1]), int(row[2]), int(row[2]) - int(row[1]), True])
                self.parents_list[parent_index].append([row[0], int(row[1]), start_time, int(row[2]), end_time, int(row[2]) - int(row[1]), duration, True])
                rows = rows + 1
        print("end_load_data. " + str(rows) + " elements, " + str(unique) + " unique.")
        self.fill_model()

    def fill_model(self):
        #fill in the model
        print("start_fill_model")
        self.model.clear()
        for i in range(len(self.parents_list)):
            # the iter piter is returned when appending the author in the first column
            # and False in the second
            piter = self.model.append(None, [self.parents_list[i][0], 0, "", 0, "", 0, "", True])
            # append the books and the associated boolean value as children of
            # the author
            j = 1
            while j < len(self.parents_list[i]):
                self.model.append(piter, self.parents_list[i][j])
                j += 1
        print("end_fill_model")


    def contains(self, search_str, mylist):
        i = 0
        for sublist in mylist:
            if sublist[0] == search_str:
                return i
            i = i + 1
        return -1
 
    def date_filter_func(self, model, iter):
        if(model[iter][7]):
            return True
        return False

    def child_filter_func(self, model, iter):
        if model[self.parent_iter][0] == model[iter][0]:
            return True
        else:
            return False

    def on_filter_date_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            value = model[tree_iter][0]
            self.date_filter_value = value
            self.apply_date_filter(self.model, self.filterText.get_text())
            #self.apply_name_filter(self.model, self.filterText.get_text())
            self.date_filter.refilter()
            self.childFilter.refilter()

    def on_applybtn_release(self, btn):
        self.apply_date_filter(self.model, self.filterText.get_text())
        self.date_filter.refilter()
        self.childFilter.refilter()

    def apply_date_filter(self, store, name):
        print("start_date_filter")
        self.filtered_rows = 0
        self.filtered_duration = 0
        treeiter = store.get_iter_first()
        while treeiter is not None:
            if store.iter_has_child(treeiter):
                childiter = store.iter_children(treeiter)
                while childiter is not None:
                    #init state for parent
                    parent_is_visible = False
                    #check filter conditions
                    if (time.time() - store[childiter][1]) < self.date_filter_value:
                        store[childiter][7] = True
                        parent_is_visible = True
                        self.filtered_duration = self.filtered_duration + store[childiter][5]
                        self.filtered_rows = self.filtered_rows + 1
                    else:
                        store[childiter][7] = False
                    childiter = store.iter_next(childiter)
            store[treeiter][7] = (name in store[treeiter][0]) and parent_is_visible
            treeiter = store.iter_next(treeiter)
        self.update_statusbar()
        print("end_date_filter")

    def update_statusbar(self):
        id_rows = self.statusbar.get_context_id("Total Rows")
        self.statusbar.push(id_rows, "Total Rows: " + str(self.filtered_rows) + " Total Duration: " + str(timedelta(seconds=(self.filtered_duration))))

    def onParentRowClick(self, *arg):
        self.parent_iter = self.model.get_iter(arg[1])
        self.childFilter.refilter()

def get_handlers(halcomp,builder,useropts):
    return [ExecLog(halcomp,builder,useropts)]