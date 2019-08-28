
import numpy as np


class CO2SYS(object):

"""CO2SYS version 1.1 (SEPT-2011)

 CO2SYS is a numpy-version of the original CO2SYS for DOS. 
 CO2SYS calculates and returns the state of the carbonate system of 
 oceanographic water samples, if supplied with enough input.

 Please note that his software is intended to be exactly identical to the 
 DOS and Excel versions that have been released previously, meaning that
 results obtained should be very nearly indentical for identical input.
 Additionally, several of the dissociation constants K1 and K2 that have 
 been published since the original DOS version was written are implemented.
 For a complete list of changes since version 1.0, see below.

 For much more info please have a look at:
 Lewis, E., and D. W. R. Wallace. 1998. Program Developed for
 CO2 System Calculations. ORNL/CDIAC-105. Carbon Dioxide Information
 Analysis Center, Oak Ridge National Laboratory, U.S. Department of Energy,
 Oak Ridge, Tennessee. 
 http://cdiac.ornl.gov/oceans/co2rprt.html
 """
    
    def __init__(


    %    55 - K2  input            ()          
%    56 - pK1 input            ()          
%    57 - pK2 input            ()          
%    58 - KW  input            ()          
%    59 - KB  input            ()          
%    60 - KF  input            ()          
%    61 - KS  input            ()          
%    62 - KP1 input            ()          
%    63 - KP2 input            ()          
%    64 - KP3 input            ()          
%    65 - KSi input            ()              
%    66 - K0  output           ()          
%    67 - K1  output           ()          
%    68 - K2  output           ()          
%    69 - pK1 output           ()          
%    70 - pK2 output           ()          
%    71 - KW  output           ()          
%    72 - KB  output           ()          
%    73 - KF  output           ()          
%    74 - KS  output           ()          
%    75 - KP1 output           ()          
%    76 - KP2 output           ()          
%    77 - KP3 output           ()          
%    78 - KSi output           ()              
%    79 - TB                   (umol/kgSW) 
%    80 - TF                   (umol/kgSW) 
%    81 - TS                   (umol/kgSW) 
%    82 - TP                   (umol/kgSW) 
%    83 - TSi                  (umol/kgSW)
%
%    *** SIMPLY RESTATES THE INPUT BY USER 
%
% In all the above, the terms "input" and "output" may be understood
%    to refer to the 2 scenarios for which CO2SYS performs calculations, 
%    each defined by its own combination of temperature and pressure.
%    For instance, one may use CO2SYS to calculate, from measured DIC and TAlk,
%    the pH that that sample will have in the lab (e.g., T=25 degC, P=0 dbar),
%    and what the in situ pH would have been (e.g., at T=1 degC, P=4500).
%    A = CO2SYS(2400,2200,1,2,35,25,1,0,4200,1,1,1,4,1)
%    pH_lab = A(3);  % 7.84
%    pH_sea = A(18); % 8.05
% 
%**************************************************************************
%
% This is version 1.1 (uploaded to CDIAC at SEP XXth, 2011):
%
% **** Changes since 1.01 (uploaded to CDIAC at June 11th, 2009):
% - Function cleans up its global variables when done (if you loose variables, this may be the cause -- see around line 570)
% - Added the outputting of K values
% - Implementation of constants of Cai and Wang, 1998
% - Implementation of constants of Lueker et al., 2000
% - Implementation of constants of Mojica-Prieto and Millero, 2002
% - Implementation of constants of Millero et al., 2002 (only their eqs. 19, 20, no TCO2 dependency)
% - Implementation of constants of Millero et al., 2006
% - Implementation of constants of Millero et al., 2010
% - Properly listed Sal and Temp limits for the available constants
% - added switch for using the new Lee et al., (2010) formulation of Total Borate (see KSO4CONSTANTS above)
% - Minor corrections to the GEOSECS constants (gave NaN for some output in earlier version)
% - Fixed decimal point error on [H+] (did not get converted to umol/kgSW from mol/kgSW).
% - Changed 'Hfreein' to 'Hfreeout' in the 'NICEHEADERS'-output (typo)
%
% **** Changes since 1.00 (uploaded to CDIAC at May 29th, 2009):
% - added a note explaining that all known bugs were removed before release of 1.00
%
%**************************************************************************
%
% CO2SYS originally by Lewis and Wallace 1998
% Converted to MATLAB by Denis Pierrot at
% CIMAS, University of Miami, Miami, Florida
% Vectorization, internal refinements and speed improvements by
% Steven van Heuven, University of Groningen, The Netherlands.
% Questions, bug reports et cetera: svheuven@gmail.com
%
%**************************************************************************



%**************************************************************************
% NOTHING BELOW THIS SHOULD REQUIRE EDITING BY USER!
%**************************************************************************



