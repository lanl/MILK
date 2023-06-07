function [pf] = MAUDAPFImport(fname,CS)
%MAUDAPFImport This function imports the experimental polefigure
%from the maud texture correction factors .apf 

    %Read file to text cells
    apf=readlines(fname);

    %Initial pf info objects
    allH = {};
    allR = {};
    allI = {};
    
    %Read the file
    pos=2;
    npfs=sscanf(apf{pos},'%d'); pos=pos+1;
    if npfs > 30
        npfs=30;
    end
    for i=1:npfs
        hkl=sscanf(apf{pos},'%d'); pos=pos+1;
        blocksz = sscanf(apf{pos},'%d'); pos=pos+1;
        tmp = zeros(blocksz,length(sscanf(apf{pos},'%f')));
        for j=1:blocksz
            tmp(j,:) = sscanf(apf{pos},'%f'); pos=pos+1;
        end
        theta=tmp(:,1)*degree;
        phi=tmp(:,2)*degree;
        x=sin(theta).*cos(phi);
        y=sin(theta).*sin(phi);
        z=cos(theta);
        allH{i} = Miller(hkl(1),hkl(2),hkl(3),CS);
        allR{i}=vector3d(x,y,z);
        allI{i}=tmp(:,3);
    end
    % Make pfs from read data
    pf = PoleFigure(allH,allR,allI);
end

