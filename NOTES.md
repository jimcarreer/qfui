# General Approach

* Loading of CSV Done
** Re-implement code from plugin / lua
* Get Display Done
** Blueprint navigation tree
** Layer viewer
* Get editing done

Basic layout desired:

    |------------------------------|
    |------------------------------|
    |                     |        |
    |                     |        |
    |                     |        |
    |    Layer Viewer     | BPTree |
    |                     |        |
    |                     |        |
    |                     |        |
    |------------------------------|

Floating windows for "tools" like GIMP and other complex UIs.

# Questions

* How do I make a GraphicsView scrollable / resizable to the parent widget?
* Layouts in QT in general (Grid / Column based?)

# QF Data Structure

It looks as though data from blueprints loads as the user requests it to, not
at startup of DF or when QF runs, so I should mirror that approach.

Parsing code:
https://github.com/DFHack/scripts/blob/13fbb5a84d59d43bf68ce190726192484d52e00a/internal/quickfort/parse.lua

Test Case:
https://github.com/DFHack/dfhack/blob/develop/data/blueprints/library/dreamfort.csv

* This has 84 Sections as far as I can tell from the qf gui
* This has 11? Dig Sections
* This has 24? Build Sections
* This has 6? Place Sections
* This has 2? Zone Sections
* This has 14? Query Sections
* This has 20? Meta Sections
* This has 8? Note Sections
* This has 1? Ignore Sections

This makes 86 but ignore sections are not visible, but I cannot account for the missing section.


Blueprint Properties
* Has 1 or more files
* Files can be nested in directories
* Directory names should probably be flattened in Tree View

File properties
* Has 1 or more sections

SectionRexer properties
* Has 1 label
* Has 1 mode
* Has metadata?
* Has 1 or more Layers
* Layer dimensions independent?
* Layer start location independent? 

Layer properties
* Metadata?
* Dimensions?
* Start?
* Grid

# Parser Context

The QFParser module should use a logger and log adapter to trace issues
with the file being parsed as debugs/infos/errors/warns. Specifically 
line no / cell position / char position will be important.  This should just
be extra log context updated whenever appropriate, possibly at the start of 
for loops that iterate lines and reset at the end of the relevant loop
https://docs.python.org/3/howto/logging-cookbook.html#adding-contextual-information-to-your-logging-output

# DF Hack and Lua Notes
https://github.com/DFHack/dfhack/blob/develop/library/lua/utils.lua
* utils.invert takes a list and creates a dictionary:


    {
        "first_element": 0,
        "second_element": 1
    }

Dump function for lua, put in qf common:
    
    function dumper (tbl, indent)
      if not indent then indent = 0 end
      for k, v in pairs(tbl) do
        formatting = string.rep("  ", indent) .. k .. ": "
        if type(v) == "table" then
          print(formatting)
          dumper(v, indent+1)
        elseif type(v) == 'boolean' then
          print(formatting .. tostring(v))
        else
          print(formatting .. v)
        end
      end
    end

Useful link:
https://www.mediafire.com/folder/u38qsqr1bq6wu/Community_Quickfort_Blueprints_v2

## Ideas
* Controller use signals connected to widget slots for data changes
* UI Widgets use signals connected to controller slots for user interaction
  * This can be circular, IE UI Widget signal causes data change which causes a signal that causes it to update
  * To prototype this I should probably try something simple like layer visibility
  * Define a ProjectController interface and then concrete Impl
  * Pass around "controller messages" via signals + slots
* Version Modeling (i.e. instead of models/.../ do models/v1/.../ etc)
* JSON schema validation of deserialized models
* dev script to generate schema from module


## TODOS
* ~~Everything should be snake case unless it's a QT override~~ looks done
* ~~QObject.tr to global tr until function~~ It's more complicated than this
* Multilayer visibility
  * Navigation view needs context menu for setting layer visibility / active layer
  * Navigation view needs "Visible Layer" node item so user can see visible layers
    at a glance
  * Visible layers should probably have adjustable alpha settings
  * Visibility / alphas can be properties under the visibility node
  * Layer viewer needs to handle multilayer visibility.
    * Viewer should have a global grid that is the smallest grid that
      completely encompasses all visible layers (take max width / height)
    * Only the active layer's grid should be drawn with solid lines