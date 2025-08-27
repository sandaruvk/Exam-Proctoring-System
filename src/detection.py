import time
import audio
import head_pose
import matplotlib.pyplot as plt
import numpy as np


PLOT_WINDOW_SIZE = 200        # number of data points to show on the live graph
CHEATING_THRESHOLD = 0.6 

#VARIABLES
is_cheeating_flag = 0
cheating_probability = 0
time_axis = list(range(PLOT_WINDOW_SIZE))
probability_history = [0] * PLOT_WINDOW_SIZE

def smooth_probability(current_value,previous_value):
    
    if previous_value > 1:
        return 0.65
    if current_value == 0:
        if previous_value < 0.01:
            return 0.01
        return previous_value / 1.01
    if previous_value == 0:
        return current_value
    return 1 * previous_value + 0.1 * current_value


#DETECTION LOGIC
def update_cheating_probability(): 
    """
    this if gonna Updates cheating probability based on head pose & audio signals.
    Sets the global cheating flag if probability crosses threshold.
    """

    global is_cheeating_flag,cheating_probability

    #IF CURRENTLY NOT CHEATING
    if is_cheeating_flag == 0:
        if head_pose.X_AXIS_CHEAT == 0:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.2, cheating_probability)
            else:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0.2, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.4, cheating_probability)
        else:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0.1, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.4, cheating_probability)
            else:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0.15, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.25, cheating_probability)

    #IF CURRENTLY  CHEATING   
    else:
        if head_pose.X_AXIS_CHEAT == 0:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.55, cheating_probability)
            else:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0.55, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.85, cheating_probability)
        else:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0.6, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.85, cheating_probability)
            else:
                if audio.AUDIO_CHEAT == 0:
                    cheating_probability = smooth_probability(0.5, cheating_probability)
                else:
                    cheating_probability = smooth_probability(0.85, cheating_probability)

    #UPDATING THE CHEATING FLAG BASED ON THE THRESHOLD
    if cheating_probability > CHEATING_THRESHOLD:
        is_cheeating_flag = 1
        print ("CHEATING DETECTED!")
    else:
        is_cheeating_flag = 0

    print(f"Cheating Probability: {cheating_probability:.2f} | Flag: {is_cheeating_flag}") 


#LIVE DETECTION AND PLOTTING
def run_live_detection():
    global time_axis,probability_history

    plt.show()
    axes = plt.gca()
    axes.set_xlim(0,PLOT_WINDOW_SIZE)
    axes.set_ylim(0,1)

    line, = axes.plot(time_axis,probability_history,'r-')
    plt.title("Suspicious Behaviour Detection")
    plt.xlabel("Time(steps)")
    plt.ylabel("Cheating Probability")

    while True:
        #THIS WILL UPDATE THE PROBABILITY HISTORY
        probability_history.pop(0)
        probability_history.append(cheating_probability)

        line.set_xdata(time_axis)
        line.set_ydata(probability_history)

        plt.draw()
        plt.pause(1e-17)
        time.sleep(0.2)

        update_cheating_probability()

