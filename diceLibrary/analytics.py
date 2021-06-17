from bokeh.plotting import figure, output_file
from bokeh.models import HoverTool
from bokeh.transform import dodge
from bokeh.layouts import gridplot
from diceLibrary.cascadeDatabase import cascadeDatabase
from bokeh.io import show, save
from bokeh.transform import transform
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource
from diceLibrary.settings import ProfilerConfig, AnalyticsConfig
from bokeh.palettes import Viridis256
from bokeh.embed import file_html
from bokeh.resources import CDN


import logging
class Analytics:
    log=None
    data=None
    runIds=None
    color={
        'dataSize': '#79D151',
        'runTime': 'darkslategray',
        'batteryTime': 'paleturquoise',
        'latency': 'gold',
        'upload': 'deepskyblue',
        'download': 'firebrick',
        'ping': 'peachpuff',
        'userCPU': 'thistle',
        'systemCPU': 'mediumpurple',
        'idleCPU': 'blueviolet',
    }
    colors=['#440154', '#30678D', '#35B778', '#FDE724','#440154', '#30678D', '#35B778','#29788E', '#22A784', '#79D151']
    legend={
        'dataSize': 'Data Size',
        'runTime': 'Run Time',
        'batteryTime': 'Battery Time',
        'latency': 'Latency',
        'upload': 'Upload',
        'download': 'Download',
        'ping': 'Ping',
        'userCPU': 'User CPU',
        'systemCPU': 'System CPU',
        'idleCPU': 'Idle CPU',
    }
    offloadColor=['black','firebrick']
    offloadLine=['solid','dashed']
    offloadLegend=['Local','Remote']
    profilerConfig=None
    config=None
    def __init__(self,config):
        self.runIds=list()

        self.log=logging.getLogger()
        self.config=config

    def addToAnalytics(self, runId):
        self.log.info('Run ID: '+runId+' added to analytics')
        self.runIds.append(runId)

    def parseUpdatedConfig(self, config):
        self.profilerConfig = config

    def analyze(self, data):
        self.data=data
        if AnalyticsConfig.CURRENTRUN in self.config:
            singleRun=self.data[self.data['runId'].isin(self.runIds)]
            singleRun=singleRun.groupby(['functionName']).mean()
            singleRun['functionName'] = singleRun.index
            self.singleRunAnalytics(singleRun)
            self.log.info('Current Run Analytics Generated')
            #self.correlationGraph(singleRun)
            #self.log.info('Current Run Correlation Graph Generated')
        else:
            self.log.warning('Current Run Analytics Not Generated')
        if AnalyticsConfig.SUMMARYANALYTICS in self.config:
            self.summaryAnalytics(data)
            self.log.info('Summary Analytics Generated')
            #self.correlationGraph(data)
            self.log.info('Summary Correlation Graph Generated')
        else:
            self.log.warning('Summary Analytics Not Generated')


    def singleRunAnalytics(self,singleRun):
        output_file('templates/single_run_plots.html')
        plots=list()
        funcNames=list(set(singleRun.functionName))
        if len(funcNames)<=0:
            self.log.warning('No function data available. Single Run Analytics Aborted')
            return
        #runTime
        if ProfilerConfig.RUNTIME in self.profilerConfig:
            runTime=list(singleRun['runTime'])
            data={'xAxis':funcNames,'runTime':runTime}
            xOffset=0
            legend=['Run Time']
            title='Function v Run Time'

            #Separately saving runtime graphs in a html file
            html_run = file_html(self.createBarChart(data, xOffset, legend, title, palette=True), CDN, 'something')
            file = open('templates/runtime.html', 'w')
            for line in html_run:
                file.write(line)

            plots.append(self.createBarChart(data,xOffset,legend,title, palette=True))

        #Battery Time
        if ProfilerConfig.ENERGY in self.profilerConfig:
            batteryTime=list(singleRun['batteryTime'])
            data2={'xAxis':funcNames,'batteryTime':batteryTime}
            xOffset2=0
            legend2=['Battery Time']
            title2='Function v Battery Time'

            #Separately saving battery graphs in a html file
            html_battery = file_html(self.createBarChart(data2,xOffset2,legend2,title2, palette=True,offset=1), CDN, 'something')
            file = open('templates/energy.html', 'w')
            for line in html_battery:
                file.write(line)

            plots.append(self.createBarChart(data2,xOffset2,legend2,title2, palette=True,offset=1))

        #Network Stats
        if ProfilerConfig.NETWORK in self.profilerConfig:
            nwStats=['upload','download','latency','ping']
            data3={'xAxis':funcNames}
            xOffset=-0.25

            for stat in nwStats:
                xList=list()
                for f in funcNames:
                    xList.append(list(singleRun[singleRun.functionName==f][stat])[0])
                data3[stat]=xList
            plots.append(self.createBarChart(data3,xOffset,nwStats,'Network Stats v Functions',500))

            # Separately saving network graphs and CPU graphs in a html file
            html_network = file_html(self.createBarChart(data3, xOffset, nwStats, 'Network Stats v Functions', 500),
                                     CDN,
                                     'something')
            file = open('templates/network.html', 'w')
            for line in html_network:
                file.write(line)


        #CPU Stats
        if ProfilerConfig.CPU in self.profilerConfig:
            cpuStats=['userCPU','systemCPU','idleCPU']
            cpuTotal = singleRun['userCPU']+singleRun['idleCPU']+singleRun['systemCPU']
            data4={'xAxis':funcNames}
            xOffset=-0.25

            # Separately saving CPU graphs in a html file
            for stat in cpuStats:
                xList=list()
                for f in funcNames:
                    xList.append(list(singleRun[singleRun.functionName==f][stat])[0])
                data4[stat]=xList
            plots.append(self.createBarChart(data4,xOffset,cpuStats,'CPUStats v Functions',500))
        grid = gridplot(plots, ncols=2)

        html_cpu = file_html(self.createBarChart(data4, xOffset, cpuStats, 'CPUStats v Functions', 500), CDN,
                             'something')
        file = open('templates/cpu.html', 'w')
        for line in html_cpu:
            file.write(line)

        save(grid)

    def summaryAnalytics(self,data):
        # prepare some data
        output_file('templates/plots.html')
        #curdoc().theme = 'dark_minimal'
        funcNames=list(set(data.functionName))
        if len(funcNames)<=0:
            self.log.warning('No function data available. Summary Analytics Aborted')
            return
        plots=list()
        for yAxis in ['dataSize','latency']:
            for stat in ['runTime','batteryTime','latency','upload','download','ping','userCPU','systemCPU','idleCPU']:
                for f in funcNames:
                    fdata=data[data.functionName==f]
                    xlocalsize=list(fdata[fdata.offloadStatus==0][yAxis])
                    xremotesize=list(fdata[fdata.offloadStatus==1][yAxis])
                    ylocaltime=list(fdata[fdata.offloadStatus==0][stat])
                    yremotetime=list(fdata[fdata.offloadStatus==1][stat])
                    x=[xlocalsize,xremotesize]
                    y=[ylocaltime,yremotetime]
                    p=self.createLineChart(x,y,f+' '+self.legend[stat]+' vs '+self.legend[yAxis],[yAxis,stat])
                    plots.append(p)
        grid = gridplot(plots, ncols=5, plot_width=300, plot_height=300)
        save(grid)

    def createLineChart(self,x,y,title,label):
        # create a new plot with a title and axis labels
        p = figure(plot_height=400,
                   plot_width=400,
                   title=title,
                   toolbar_location="below",
                   x_axis_label=self.legend[label[0]],
                   y_axis_label=self.legend[label[1]],
                   tools="pan,wheel_zoom,box_zoom,tap,reset,undo,redo,save")
        # add multiple renderers
        for idx, i in enumerate(x):
            p.line(i, y[idx], legend_label=self.offloadLegend[idx], line_color=self.offloadColor[idx], line_width=2,line_dash=self.offloadLine[idx])
            p.legend.location = "top_left"
            p.legend.click_policy="hide"
        # show the results
        return p

    def createBarChart(self,data,xOffset,legend, title, size=400, palette=False,offset=0):
        plt = figure(plot_height=size,
                     plot_width=size,
                     title=title,
                     toolbar_location="below",
                     x_range=data['xAxis'],
                     tools="pan,wheel_zoom,box_zoom,tap,reset,undo,redo,save")
        idx=-1
        for key, value in data.items():
            idx=idx+1
            if idx==0:
                continue
            #Plotting
            plt.vbar(x = dodge('xAxis', xOffset, range = plt.x_range),                            #categories
                     top = key,                      #bar heights
                     width = .20,
                     fill_alpha = .5,
                     fill_color = self.color.get(key,(0,0,0)) if palette==False else self.colors[idx+offset%10],
                     source=data,
                     legend_label=legend[idx-1]
                     )
            xOffset=xOffset+0.20
        tooltips = [
            ('Function Name', data['xAxis'][0]),
        ]
        plt.add_tools(HoverTool(tooltips=tooltips))
        #Signing the axis
        plt.xaxis.axis_label="Functions"
        plt.yaxis.axis_label="Runtime"
        plt.legend.location = "top_left"
        plt.legend.click_policy="hide"
        return plt

    def correlationGraph(self,data):
        data['local'] = data.apply(lambda row: 1-row.offloadStatus, axis=1)
        data['remote'] = data.apply(lambda row: row.offloadStatus, axis=1)
        #Now we will create correlation matrix using pandas
        df = data.corr()
        df=df.drop(['offloadStatus','dataSize','runTime','batteryTime','latency','upload','download','ping','userCPU','systemCPU','idleCPU'], errors = 'ignore')
        df=df.drop(['offloadStatus','local','remote'], axis=1)
        df.index.name = 'AllColumns1'
        df.columns.name = 'AllColumns2'

        # Prepare data.frame in the right format
        df = df.stack().rename("value").reset_index()

        # here the plot :
        output_file("CorrelationPlot.html")

        # You can use your own palette here
        # colors = ['#d7191c', '#fdae61', '#ffffbf', '#a6d96a', '#1a9641']

        # I am using 'Viridis256' to map colors with value, change it with 'colors' if you need some specific colors
        mapper = LinearColorMapper(
            palette=Viridis256, low=df.value.min(), high=df.value.max())

        # Define a figure and tools
        TOOLS = "box_select,lasso_select,pan,wheel_zoom,box_zoom,reset,help"
        p = figure(
            tools=TOOLS,
            plot_width=1000,
            plot_height=600,
            title="Correlation plot",
            x_range=list(df.AllColumns1.drop_duplicates()),
            y_range=list(df.AllColumns2.drop_duplicates()),
            toolbar_location="right",
            x_axis_location="below")

        # Create rectangle for heatmap
        p.rect(
            x="AllColumns1",
            y="AllColumns2",
            width=1,
            height=1,
            source=ColumnDataSource(df),
            line_color=None,
            fill_color=transform('value', mapper))

        # Add legend
        color_bar = ColorBar(
            color_mapper=mapper,
            location=(0, 0),
            ticker=BasicTicker(desired_num_ticks=10))

        p.add_layout(color_bar, 'right')

        show(p)

if __name__=='__main__':
    runIds=['06/03/2021T00:21:59','06/03/2021T00:22:07','06/03/2021T00:21:29','06/03/2021T00:22:46']
    dB=cascadeDatabase('store.db')
    dB.createTableIfNotExists()
    #dB.addCascadeEntry('func1',False,28,29,34,45,46,56,34,6,7,8,9,10)
    data=dB.getCascadeData()
    singleRun=data[data['runId'].isin(runIds)]
    singleRun=singleRun.groupby(['functionName']).mean()
    singleRun['functionName'] = singleRun.index
    analytics=Analytics()
    analytics.singleRunAnalytics(singleRun)
    analytics.summaryAnalytics(data)

    analytics.correlationGraph(data)

