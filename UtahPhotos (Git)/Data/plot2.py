import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('TrainedData.csv')
#df = pd.read_csv('merged.csv')
#df = pd.read_csv('../trist/UtahPhotos/Data/raw_data.csv')

"""
##El vs. Az & CalcEl, CalcAz; Note that Az and El for JUNE datasets are current

f, (ax1, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w')
ax1.set_xlim(-5, 90)
ax2.set_xlim(90, 365)
ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.yaxis.tick_left()
ax2.tick_params(labelleft='on')
ax2.yaxis.tick_right()

kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Current Coordinates')
ax1.scatter(df['CalcAz'], df['CalcEl'], color='red', marker='o', s=5, label='Manual Offset Coordinates')
ax1.scatter(df['CalcFlux Az'], df['CalcFlux El'], color='magenta', marker='o', s=5, label='AutoFlux Offset Coordinates')
ax1.scatter(df['CalcArea Az'], df['CalcArea El'], color='purple', marker='o', s=5, label='AutoArea Offset Coordinates')
ax2.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Current Coordinates')
ax2.scatter(df['CalcAz'], df['CalcEl'], color='red', marker='o', s=5, label='Manual Offset Coordinates')
ax2.scatter(df['CalcFlux Az'], df['CalcFlux El'], color='magenta', marker='o', s=5, label='AutoFlux Offset Coordinates')
ax2.scatter(df['CalcArea Az'], df['CalcArea El'], color='purple', marker='o', s=5, label='AutoArea Offset Coordinates')

##cut marks to indicate a break
d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((1-d, 1+d), (-d, +d), **kwargs)
ax1.plot((1-d, 1+d), (1-d, 1+d), **kwargs)
kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1-d, 1+d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)
ax1.set_ylabel('El')
ax1.set_xlabel('Az')

plt.title('Gamma Bootes Offset')
ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()
plt.savefig('Overlay Methods.png')
plt.close()
"""
"""
##Nominal, Skycam, and True
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w')
ax1.set_xlim(0, 70)
ax2.set_xlim(290, 360)
ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.yaxis.tick_left()
ax2.tick_params(labelleft='on')
ax2.yaxis.tick_right()

kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.scatter(df['TrueAz'], df['TrueEl'], color='green', marker='o', s=5, label='True Coordinates')
ax1.scatter(df['Nominal Az'], df['Nominal El'], color='purple', marker='o', s=5, label='Nominal Coordinates')
ax1.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')
ax2.scatter(df['TrueAz'], df['TrueEl'], color='green', marker='o', s=5, label='True Coordinates')
ax2.scatter(df['Nominal Az'], df['Nominal El'], color='purple', marker='o', s=5, label='Nominal Coordinates')
ax2.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')

ax1.quiver(
    df['CalcAz'],
    df['CalcEl'],
    df['Az'] - df['CalcAz'],   # dx
    df['El'] - df['CalcEl'],   # dy
    angles='xy',
    scale_units='xy',
    scale=1,
    color='black',
    width=0.006
)

ax2.quiver(
    df['CalcAz'],
    df['CalcEl'],
    df['Az'] - df['CalcAz'],   # dx
    df['El'] - df['CalcEl'],   # dy
    angles='xy',
    scale_units='xy',
    scale=1,
    color='black',
    width=0.006
)

##cut marks to indicate a break
d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((1-d, 1+d), (-d, +d), **kwargs)
ax1.plot((1-d, 1+d), (1-d, 1+d), **kwargs)
kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1-d, 1+d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)
ax1.set_ylabel('El')
ax1.set_xlabel('Az')

plt.title('Gamma Bootes Offset')
ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()
plt.savefig('Nominal, Skycam, & True.png')
plt.close()
"""
"""
#Skycam and Offset
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w')
ax1.set_xlim(-1, 180)
ax2.set_xlim(180, 361)
ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.yaxis.tick_left()
ax2.tick_params(labelleft='on')
ax2.yaxis.tick_right()

kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')
#ax1.scatter(df['Calc Az'], df['Calc El'], color='red', marker='o', s=5, label='Offset Coordinates')
ax2.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')
#ax2.scatter(df['Calc Az'], df['Calc El'], color='red', marker='o', s=5, label='Offset Coordinates')

Scale = 4
ax1.quiver(
    df['Az'],
    df['El'],
    (df['Calc Az'] - df['Az']) * Scale,   
    (df['Calc El'] - df['El']) * Scale,   
    angles='xy',
    scale_units='xy',
    scale=1,
    color='black',
    width=0.006
)

ax2.quiver(
    df['Az'],
    df['El'],
    (df['Calc Az'] - df['Az']) * Scale,   
    (df['Calc El'] - df['El']) * Scale,   
    angles='xy',
    scale_units='xy',
    scale=1,
    color='black',
    width=0.006
)


##cut marks to indicate a break
d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((1-d, 1+d), (-d, +d), **kwargs)
ax1.plot((1-d, 1+d), (1-d, 1+d), **kwargs)
kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1-d, 1+d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)
ax1.set_ylabel('El')
ax1.set_xlabel('Az')

plt.title('Gamma Bootes Offset')
ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()
plt.savefig('Skycam_&_Offset.png')
plt.close()
"""

"""
##Nominal Offset Plot
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w')
ax1.set_xlim(0, 70)
ax2.set_xlim(290, 360)
ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.yaxis.tick_left()
ax2.tick_params(labelleft='on')
ax2.yaxis.tick_right()

kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.scatter(df['CalcAzNom'], df['CalcElNom'], color='magenta', marker='o', s=5, label='Nominal Offset Coordinates')
ax1.scatter(df['Nominal Az'], df['Nominal El'], color='purple', marker='o', s=5, label='Nominal Coordinates')
ax1.scatter(df['CalcAz'], df['CalcEl'], color='red', marker='o', s=5, label='Offset Coordinates')
ax1.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')
ax2.scatter(df['CalcAzNom'], df['CalcElNom'], color='magenta', marker='o', s=5, label='Nominal Offset Coordinates')
ax2.scatter(df['Nominal Az'], df['Nominal El'], color='purple', marker='o', s=5, label='Nominal Coordinates')
ax2.scatter(df['CalcAz'], df['CalcEl'], color='red', marker='o', s=5, label='Offset Coordinates')
ax2.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')

ax1.quiver(
    df['CalcAzNom'],
    df['CalcElNom'],
    df['Nominal Az'] - df['CalcAzNom'],   # dx
    df['Nominal El'] - df['CalcElNom'],   # dy
    angles='xy',
    scale_units='xy',
    scale=1,
    color='black',
    width=0.006
)

ax2.quiver(
    df['CalcAzNom'],
    df['CalcElNom'],
    df['Nominal Az'] - df['CalcAzNom'],   # dx
    df['Nominal El'] - df['CalcElNom'],   # dy
    angles='xy',
    scale_units='xy',
    scale=1,
    color='black',
    width=0.006
)

##cut marks to indicate a break
d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((1-d, 1+d), (-d, +d), **kwargs)
ax1.plot((1-d, 1+d), (1-d, 1+d), **kwargs)
kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1-d, 1+d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)
ax1.set_ylabel('El')
ax1.set_xlabel('Az')

plt.title('Gamma Bootes Offset')
ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()
plt.savefig('Nominal, Skycam, & Their Offsets.png')
plt.close()


#Current Plot (vs. true... compare with Nominal One also)
f, (ax1, ax2) = plt.subplots(1, 2, sharey=True, facecolor='w')
ax1.set_xlim(0, 70)
ax2.set_xlim(290, 360)
ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.yaxis.tick_left()
ax2.tick_params(labelleft='on')
ax2.yaxis.tick_right()

kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.scatter(df['Current Az'], df['Current El'], color='orange', marker='o', s=5, label='Current Coordinates')
ax1.scatter(df['TrueAz'], df['TrueEl'], color='green', marker='o', s=5, label='True Coordinates')
#ax1.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')
ax2.scatter(df['Current Az'], df['Current El'], color='orange', marker='o', s=5, label='Current Coordinates')
ax2.scatter(df['TrueAz'], df['TrueEl'], color='green', marker='o', s=5, label='True Coordinates')
#ax2.scatter(df['Az'], df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')

##cut marks to indicate a break
d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((1-d, 1+d), (-d, +d), **kwargs)
ax1.plot((1-d, 1+d), (1-d, 1+d), **kwargs)
kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1-d, 1+d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)
ax1.set_ylabel('El')
ax1.set_xlabel('Az')

plt.title('Gamma Bootes Offset')
ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()
plt.savefig('Current, Skycam, & True.png')
plt.close()
"""








"""

##Plots for Trained Data
#For CalculatedOffsets
plt.scatter(df['May Az'], df['May El'], color='blue', marker='o', s=5, label= 'May')
#plt.scatter(df['May Calc Az'], df['May Calc El'], color='red', marker='o', s=5, label= 'May Calc')
plt.scatter(df['June Az'], df['June El'], color='green', marker='o', s=5, label= 'June')
#plt.scatter(df['June Calc Az'], df['June Calc El'], color='orange', marker='o', s=5, label= 'June Calc')
plt.xlabel('Azimuth (degree)')
plt.ylabel('Elevation (degree)')
plt.title("Actual Offsets - 8x Scale")
plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()


Scale = 8
plt.quiver(
    df['May Az'],
    df['May El'],
    (df['May Calc Az'] - df['May Az']) * Scale,   
    (df['May Calc El'] - df['May El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.quiver(
    df['June Az'],
    df['June El'],
    (df['June Calc Az'] - df['June Az']) * Scale,   
    (df['June Calc El'] - df['June El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.savefig('CalcOffsets.png')
plt.close()
"""

#For Predicted Offsets
plt.scatter(df['May Az'], df['May El'], color='blue', marker='o', s=5, label= 'May')
#plt.scatter(df['May PrAz'], df['May PrEl'], color='red', marker='o', s=5, label= 'May Bending')
#plt.scatter(df['May Calc Az'], df['May Calc El'], color='red', marker='o', s=5, label= 'May Calc')
plt.scatter(df['June Az'], df['June El'], color='green', marker='o', s=5, label= 'June')
#plt.scatter(df['June PrAz'], df['June PrEl'], color='orange', marker='o', s=5, label= 'June Bending')
#plt.scatter(df['June Calc Az'], df['June Calc El'], color='orange', marker='o', s=5, label= 'June Calc')
plt.xlabel('Azimuth (degree)')
plt.ylabel('Elevation (degree)')
plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.title("Predicted Offsets - 8x Scale")
plt.legend()

Scale = 8
plt.quiver(
    df['May Az'],
    df['May El'],
    (df['May PrAz'] - df['May Az']) * Scale,   
    (df['May PrEl'] - df['May El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.quiver(
    df['June Az'],
    df['June El'],
    (df['June PrAz'] - df['June Az']) * Scale,   
    (df['June PrEl'] - df['June El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)


plt.savefig('Predicted Offsets.png')
plt.close()
#"""
"""

#For Notebook Bend Offsets
plt.scatter(df['May Az'], df['May El'], color='blue', marker='o', s=5, label= 'May')
#plt.scatter(df['May Calc Az'], df['May Calc El'], color='red', marker='o', s=5, label= 'May Calc')
plt.scatter(df['June Az'], df['June El'], color='green', marker='o', s=5, label= 'June')
#plt.scatter(df['June Calc Az'], df['June Calc El'], color='orange', marker='o', s=5, label= 'June Calc')
plt.xlabel('Azimuth (degree)')
plt.ylabel('Elevation (degree)')
plt.title("CTBend Offsets - 8x Scale")
plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()


Scale = 8
plt.quiver(
    df['May Az'],
    df['May El'],
    (df['May Bend Az'] - df['May Az']) * Scale,   
    (df['May Bend El'] - df['May El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.quiver(
    df['June Az'],
    df['June El'],
    (df['June Bend Az'] - df['June Az']) * Scale,   
    (df['June Bend El'] - df['June El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.savefig('NewBendOffsets.png')
plt.close()
"""

"""

#For NEWBEND Residuals Plot
plt.scatter(df['May Az'], df['May El'], color='blue', marker='o', s=5, label= 'May')
#plt.scatter(df['May Calc Az'], df['May Calc El'], color='red', marker='o', s=5, label= 'May Calc')
plt.scatter(df['June Az'], df['June El'], color='green', marker='o', s=5, label= 'June')
#plt.scatter(df['June Calc Az'], df['June Calc El'], color='orange', marker='o', s=5, label= 'June Calc')
plt.xlabel('Azimuth (degree)')
plt.ylabel('Elevation (degree)')
plt.title("NewBend Residuals - 32x Scale")
plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()
plt.suptitle("RMS El = 0.04502, RMS Az = 0.01967", color='gray')


Scale = 32
plt.quiver(
    df['May Az'],
    df['May El'],
    (df['May Bend ResAz'] - df['May Az']) * Scale,   
    (df['May Bend ResEl'] - df['May El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.quiver(
    df['June Az'],
    df['June El'],
    (df['June Bend ResAz'] - df['June Az']) * Scale,   
    (df['June Bend ResEl'] - df['June El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.savefig('NewCTBendResiduals.png')
plt.close()
"""


#"""


#For Residuals Plot
plt.scatter(df['May Az'], df['May El'], color='blue', marker='o', s=5, label= 'May')
#plt.scatter(df['May Calc Az'], df['May Calc El'], color='red', marker='o', s=5, label= 'May Calc')
plt.scatter(df['June Az'], df['June El'], color='green', marker='o', s=5, label= 'June')
#plt.scatter(df['June Calc Az'], df['June Calc El'], color='orange', marker='o', s=5, label= 'June Calc')
plt.xlabel('Azimuth (degree)')
plt.ylabel('Elevation (degree)')
plt.title("Residuals - 100x Scale")
plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()
plt.suptitle("RMS El = 0.0116, RMS Az = 0.008", color='gray')


Scale = 100
plt.quiver(
    df['May Az'],
    df['May El'],
    (df['May ResAz'] - df['May Az']) * Scale,   
    (df['May ResEl'] - df['May El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.quiver(
    df['June Az'],
    df['June El'],
    (df['June ResAz'] - df['June Az']) * Scale,   
    (df['June ResEl'] - df['June El']) * Scale,   
    color='black',
    width=0.003,
    angles='xy',
    scale_units='xy',
    scale=.75
)

plt.savefig('Residuals.png')
plt.close()
#"""



"""
#TEST TEST TEST TEST TEST
#Calc
plt.scatter(df['Az'], df['El'], color='blue', marker='o', s=5, label= 'Scale = 4x')
plt.xlabel('Azimuth (degree)')
plt.ylabel('Elevation (degree)')
plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()

Scale = 4
plt.quiver(
    df['Az'],
    df['El'],
    (df['Calc Az'] - df['Az']) * Scale,   
    (df['Calc El'] - df['El']) * Scale,   
    color='black',
    width=0.003
)
plt.savefig('CalcOffsetsTogether.png')
plt.close()

#Bend
plt.scatter(df['Az'], df['El'], color='blue', marker='o', s=5, label= 'Scale = 4x')
plt.xlabel('Azimuth (degree)')
plt.ylabel('Elevation (degree)')
plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
plt.legend()

Scale = 4
plt.quiver(
    df['Az'],
    df['El'],
    (df['Bend Az'] - df['Az']) * Scale,   
    (df['Bend El'] - df['El']) * Scale,   
    color='black',
    width=0.003
)

plt.savefig('BendOffsetsTogether.png')
plt.close()
"""




"""
##Az, El histogram
plt.hist([df['Offset |Az|'], df['Offset |El|']], bins=40, stacked=True, 
         label=['Offset |Az|', 'Offset |El|'], edgecolor='black', 
         color=['green', 'yellow'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('Offset; Absolute Azimuth & Elevation.png')
plt.close()


##|d| histogram
plt.hist([df['|d|']], bins=40, stacked=True, 
         label=['|d|'], edgecolor='black', 
         color=['lime'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('Offset v. Uncertainty; distance.png')
plt.close()
"""

"""
##Residuals histograms
plt.hist([df['|El| Residuals'], df['|Az| Residuals']], bins=40, stacked=True, 
         label=['|El| Residuals', '|Az| Residuals'], edgecolor='black', 
         color=['red', 'royalblue'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('Az and El Residuals.png')
plt.close()
"""

"""
##|d| histogram
plt.hist([df['|d|'], df['Uncertainty |d|']], bins=40, stacked=True, 
         label=['|d|', 'Uncertainty |d|'], edgecolor='black', 
         color=['red', 'royalblue'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('Offset v. Uncertainty; Distance.png')
plt.close()
"""

"""
#El, Az & TrueEl, TrueAz
plt.scatter(df['Az'] , df['El'], color='royalblue', marker='o', s=5, label='Skycam Coordinates')
plt.scatter(df['TrueAz'], df['TrueEl'], color='green', marker='o', s=5, label='True Coordinates')
plt.xlabel('Az')
plt.ylabel('El')
plt.title('Gamma Bootes True')
plt.legend()
plt.grid(True, axis='both', linestyle='--', color='gray', linewidth=0.5)
plt.savefig('TrueAz_v_TrueEl.png')
plt.close()

#CalcEl, CalcAz & TrueEl, Truez
plt.scatter(df['CalcAz'], df['CalcEl'], color='red', marker='o', s=5, label='Offset Coordinates')
plt.scatter(df['TrueAz'], df['TrueEl'], color='green', marker='o', s=5, label='True Coordinates')
plt.xlabel('Az')
plt.ylabel('El')
plt.title('Gamma Bootes True v. Offset')
plt.legend()
plt.grid(True, axis='both', linestyle='--', color='gray', linewidth=0.5)
plt.savefig('True_&_Offset.png')
plt.close()

##El Plots
plt.scatter(df['El'], df['CalcEl'], color='royalblue', marker='o', s=5, label='El v. CalcEL')
plt.scatter(df['El'], df['TrueEl'], color='red', marker='o', s=5, label='El v. TrueEl')
plt.xlabel('El')
plt.ylabel('Chosen_El')
plt.title('Gamma Bootes - El')
plt.legend()
plt.grid(True, axis='both', linestyle='--', color='gray', linewidth=0.5)
plt.savefig('El_Plots.png')
plt.close()


##Az Plots
plt.scatter(df['Az'], df['CalcAz'], color='royalblue', marker='o', s=5, label='Az v. CalcAz')
plt.scatter(df['Az'], df['TrueAz'], color='red', marker='o', s=5, label='Az v. TrueAz')
plt.xlabel('Az')
plt.ylabel('Chosen_Az')
plt.title('Gamma Bootes - Az')
plt.legend()
plt.grid(True, axis='both', linestyle='--', color='gray', linewidth=0.5)
plt.savefig('Az_Plots.png')
plt.close()


##Histogram attempts; add uncertainties at some point
plt.hist([df['Offset Distance'], df['Uncertainty Distance']], bins=20, stacked=True, 
         label=['Offset Distance', 'Uncertainty Distance'], edgecolor='black', 
         color=['red', 'royalblue'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('Offset v. Uncertainty Distance.png')
plt.close()

plt.hist([df['TrueOffset Distance'], df['Uncertainty Distance']], bins=20, stacked=True, 
         label=['TrueOffset Distance', 'Uncertainty Distance'], edgecolor='black',
         color=['green', 'royalblue'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('TrueOffset v. Uncertainty Distance.png')
plt.close()

plt.hist(df['Uncertainty Distance'], bins=20, stacked=True, 
         label=['Uncertainty Distance'], edgecolor='black',
         color=['royalblue'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('Uncertainty Distance.png')
plt.close()

plt.hist(df['Offset Distance'], bins=20, stacked=True, 
         label=['Offset Distance'], edgecolor='black',
         color=['red'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('Offset Distance.png')
plt.close()

plt.hist(df['TrueOffset Distance'], bins=20, stacked=True, 
         label=['TrueOffset Distance'], edgecolor='black',
         color=['green'])
plt.title("Distribution of Column Data")
plt.legend()
plt.xlabel("Degrees")
plt.ylabel("Frequency")
plt.savefig('TrueOffset Distance.png')
plt.close()
"""