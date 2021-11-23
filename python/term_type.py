try:
    import curses
except:
    out = ""
    out += "Could not import module 'curses'. If you you are on windows, you "
    out += "need to run 'pip install windows-curses' because python does not "
    out += "have curses automatically installed on windows for some reason."
    print(out)
    raise

from random import randint
import time

# =============================================================================
# Helper Functions
# -----------------------------------------------------------------------------

def yx(x, y=None):
    """
    Translate xy coordinates to ncurses' coordinates so you don't go insane
        while using ncurses and its cursed yx coordinate system.
    """
    if y is None:
        return x[1], x[0]
    else:
        return y, x

# =============================================================================
# Helper Classes
# -----------------------------------------------------------------------------

class PracticeTextEdit:
    def __init__(self, window, target_text, typed_text=""):
        self.window = window
        self.target_text = target_text
        self.typed_text = typed_text

    def update(self):
        """
        Checks for user input, responding to it if there is any and changing the
            window to reflect it. You must call window.clear() before you run
            this method and window.refresh() after it to actually display the
            updates.
        """
        max_x, max_y = self.window.getmaxyx()

    def edit(self):
        """
        Gives all control of this app to the TextEdit. If you just want it to
            check for user input and respond to it but not hold up the
            application so that you can do otherthings as well, call the
            check method instead.
        """

    @staticmethod
    def rows(width, text):
        """
        Returns the given text as an array of strings for the given width. Each
            index represents the text that should be displayed on that row
            assuming the text only has the given width characters to be
            displayed.
        """
        out = []
        curr_line = ""

        for ch in text:
            if ch == "\r":
                continue

            elif ch == " " and curr_line == "":
                continue # No spaces at beginning of each line

            elif ch == "\n" and len(out) == 0:
                continue # No newlines before first words

            elif ch == "\n":
                # Newline
                out.append(curr_line.rstrip())
                curr_line = ""
                continue

            elif len(curr_line) + 1 >= width:
                # Need a new line, make sure not to split up one word onto
                #   multiple lines if possible
                words = curr_line.split()

                if len(words) > 1:
                    curr_line = words.pop() + ch
                    out.append(" ".join(words))
                else:
                    out.append(curr_line.rstrip())
                    curr_line = ch
                continue

            curr_line += ch

        return out

# =============================================================================
# Main Function
# -----------------------------------------------------------------------------

def main(scr=None):
    if scr is None: curses.wrapper(main); return

def test():
    example_text = """
    In the year 1775, there stood upon the borders of Epping Forest, at a distance of about twelve miles from London--measuring from the Standard in Cornhill,' or rather from the spot on or near to which the Standard used to be in days of yore--a house of public entertainment called the Maypole; which fact was demonstrated to all such travellers as could neither read nor write (and at that time a vast number both of travellers and stay-at-homes were in this condition) by the emblem reared on the roadside over against the house, which, if not of those goodly proportions that Maypoles were wont to present in olden times, was a fair young ash, thirty feet in height, and straight as any arrow that ever English yeoman drew.

    The Maypole--by which term from henceforth is meant the house, and not its sign--the Maypole was an old building, with more gable ends than a lazy man would care to count on a sunny day; huge zig-zag chimneys, out of which it seemed as though even smoke could not choose but come in more than naturally fantastic shapes, imparted to it in its tortuous progress; and vast stables, gloomy, ruinous, and empty. The place was said to have been built in the days of King Henry the Eighth; and there was a legend, not only that Queen Elizabeth had slept there one night while upon a hunting excursion, to wit, in a certain oak-panelled room with a deep bay window, but that next morning, while standing on a mounting block before the door with one foot in the stirrup, the virgin monarch had then and there boxed and cuffed an unlucky page for some neglect of duty. The matter-of-fact and doubtful folks, of whom there were a few among the Maypole customers, as unluckily there always are in every little community, were inclined to look upon this tradition as rather apocryphal; but, whenever the landlord of that ancient hostelry appealed to the mounting block itself as evidence, and triumphantly pointed out that there it stood in the same place to that very day, the doubters never failed to be put down by a large majority, and all true believers exulted as in a victory.

    Whether these, and many other stories of the like nature, were true or untrue, the Maypole was really an old house, a very old house, perhaps as old as it claimed to be, and perhaps older, which will sometimes happen with houses of an uncertain, as with ladies of a certain, age. Its windows were old diamond-pane lattices, its floors were sunken and uneven, its ceilings blackened by the hand of time, and heavy with massive beams. Over the doorway was an ancient porch, quaintly and grotesquely carved; and here on summer evenings the more favoured customers smoked and drank--ay, and sang many a good song too, sometimes--reposing on two grim-looking high-backed settles, which, like the twin dragons of some fairy tale, guarded the entrance to the mansion.

    In the chimneys of the disused rooms, swallows had built their nests for many a long year, and from earliest spring to latest autumn whole colonies of sparrows chirped and twittered in the eaves. There were more pigeons about the dreary stable-yard and out-buildings than anybody but the landlord could reckon up. The wheeling and circling flights of runts, fantails, tumblers, and pouters, were perhaps not quite consistent with the grave and sober character of the building, but the monotonous cooing, which never ceased to be raised by some among them all day long, suited it exactly, and seemed to lull it to rest. With its overhanging stories, drowsy little panes of glass, and front bulging out and projecting over the pathway, the old house looked as if it were nodding in its sleep. Indeed, it needed no very great stretch of fancy to detect in it other resemblances to humanity. The bricks of which it was built had originally been a deep dark red, but had grown yellow and discoloured like an old man's skin; the sturdy timbers had decayed like teeth; and here and there the ivy, like a warm garment to comfort it in its age, wrapt its green leaves closely round the time-worn walls.

    It was a hale and hearty age though, still: and in the summer or autumn evenings, when the glow of the setting sun fell upon the oak and chestnut trees of the adjacent forest, the old house, partaking of its lustre, seemed their fit companion, and to have many good years of life in him yet.

    The evening with which we have to do, was neither a summer nor an autumn one, but the twilight of a day in March, when the wind howled dismally among the bare branches of the trees, and rumbling in the wide chimneys and driving the rain against the windows of the Maypole Inn, gave such of its frequenters as chanced to be there at the moment an undeniable reason for prolonging their stay, and caused the landlord to prophesy that the night would certainly clear at eleven o'clock precisely,--which by a remarkable coincidence was the hour at which he always closed his house.

    The name of him upon whom the spirit of prophecy thus descended was John Willet, a burly, large-headed man with a fat face, which betokened profound obstinacy and slowness of apprehension, combined with a very strong reliance upon his own merits. It was John Willet's ordinary boast in his more placid moods that if he were slow he was sure; which assertion could, in one sense at least, be by no means gainsaid, seeing that he was in everything unquestionably the reverse of fast, and withal one of the most dogged and positive fellows in existence--always sure that what he thought or said or did was right, and holding it as a thing quite settled and ordained by the laws of nature and Providence, that anybody who said or did or thought otherwise must be inevitably and of necessity wrong.

    Mr Willet walked slowly up to the window, flattened his fat nose against the cold glass, and shading his eyes that his sight might not be affected by the ruddy glow of the fire, looked abroad. Then he walked slowly back to his old seat in the chimney-corner, and, composing himself in it with a slight shiver, such as a man might give way to and so acquire an additional relish for the warm blaze, said, looking round upon his guests:

    'It'll clear at eleven o'clock. No sooner and no later. Not before and not arterwards.'

    'How do you make out that?' said a little man in the opposite corner. 'The moon is past the full, and she rises at nine.'

    John looked sedately and solemnly at his questioner until he had brought his mind to bear upon the whole of his observation, and then made answer, in a tone which seemed to imply that the moon was peculiarly his business and nobody else's:

    'Never you mind about the moon. Don't you trouble yourself about her. You let the moon alone, and I'll let you alone.'

    'No offence I hope?' said the little man.
    """
    print(PracticeTextEdit.rows(100, ""))

if __name__ == "__main__":
    main()





