## DNS feature presentation
### Agenda
* the meaning of feature
* current state of feature implementation
* UI Demo
  * Default - single date mode
  *  Legend
  *  spectrum
  *  tooltip 
  *  Zoom
  *  compare mode
* Show code 
  *  Backend
     *  show general structure of backend
     *  show step by step computation of average DNS availability on example of single date
     *  explain how backend connected to frontend
     *  few words about deployment
  *  Frontend 
     *  talk about react and functional paradigm in web development 
     *  briefly 
* Few words about next steps.
  * Work on fixes.
  * Propose improvements.
  * Talk about IPv6 deployemnt feature.
    * business logic 
    * UI represenation
### Implemented Feature functionality
- [x] Possiblity to check worldwide dns average availability at given date.
- [x] Possibility to compare worldwide dns average availability at given date with previous date.
- [x] Flexible UI that allows to interactively choose dates and to see availability of DNS servers at given  two dates.

### What we don't finished yet realted to the feature
  - UI still needs to be improved.
    - we need to add switch between mode of comparison of two dates and mode of showing availability at one date. Right now compare mode is default mode.
    - We need to fix buttons that are not properly alligned right now.
    - We need to reset graph state when user changes date , right now its represent previoius state of graph.
    - Color at tooltip result that represented right now as bold.
  - Data dump not implemnted yet ( button on UI ,that make it possible to download data in csv format , maybe CLI command )
  - Tests for backend .
  - Fix race conditions in frontend.
### Possible improvements.
- Runtime improvements.
  - Add possiblity to compute all the required data in advance and store it in some local database ( sqlite or something else ) , so we don't need to compute it every time user makes request , it will reduce runtime significantly.
- UI improvements
  -  Add probes data to UI , so user can see which probes used to compute average availability , locate this probes geographically on map. It will give user more information about how "precise" the average availability is. The much widespread probes are , the more precise average availability is. [Example](https://codesandbox.io/s/proportional-symbol-map-13gd32?from-embed)
  -  remove tooltip and represent all the data at the map , so user can see all the data at once , without need to hover over the map. [Example](https://codesandbox.io/s/basic-annotation-0qt1g?from-embed)
  -  Add spectrum legend , with arrow that will contains all the range of values mapped by color , once user hover over the region , arrow will point to the color that represents this value. [Intuition](https://observablehq.com/@d3/d3-scalelinear)