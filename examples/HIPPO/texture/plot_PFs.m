
% crystal symmetry
CS = crystalSymmetry('622', [2.9 2.9 4.7], 'X||a*', 'Y||b', 'Z||c*');

% specimen symmetry
SS = specimenSymmetry('1');

% plotting convention
setMTEXpref('xAxisDirection','east');
setMTEXpref('zAxisDirection','outOfPlane');
setMTEXpref('EulerAngleConvention','Matthies')
setMTEXpref('FontSize',9.2);


%Plot the gamma PFs
base_name='alpha-Ti'
for i=0
    name=[pwd sprintf('/run%03d/step_7/',i) base_name];
    pf_name = [name '.apf'];

    %% Import the Data
    % create a Pole Figure variable containing the data
    odf_name = [name '_odf.mat'];
    if isfile(odf_name)
        load([name '_odf.mat'])
    else
%         pf = PoleFigure.load(fname,CS,SS,'interface','beartex');
        pf = MAUDAPFImport(pf_name,CS)
        odf =calcODF(pf,'resolution',7.5*degree,'halfwidth',10*degree,'iterMin',11)
        save(odf_name,'odf','pf','CS','SS')
    end

    figure; plot(pf{[1,2]}.normalize)
    figure; plot(pf{[1,2]}.normalize,'smooth')
    CLim(gcm,'equal');
    CLim(gcm,[0,2])
    
    figure; plotPDF(odf,{Miller(0,0,0,2,CS),Miller(1,0,-1,0,CS),Miller(1,0,-1,1,CS)},'figSize','small','minmax')
    CLim(gcm,'equal');
    CLim(gcm,[0,2])
    h=gcf
    h.Units='inches'
    hhh = findall(h,'type','text');
    hhh(5).Visible='off'
    hhh(12).Visible='off'
    hhh(19).Visible='off'
    for i=0:5
        hhh(end-i).Visible='off'
    end
    saveFigure([name '_PF.pdf'],'-fillpage')  
    save([name '_odf.mat'],'odf','CS','SS')
end



