from mop.data.projects.borderzones import project_borderzones
from mop.data.projects.barbyz import project_barbyz
from mop.data.projects.holdura import project_holdura
from mop.data.projects.idcew import project_idcew
from mop.data.projects.tarsr import project_tarsr
from mop.data.projects.vlachs import project_vlachs

project_data = {
    'idcew': project_idcew,
    'tarsr': project_tarsr,
    'barbyz_10-13': project_barbyz,
    'holdura': project_holdura,
    'borderzones': project_borderzones,
    'vlachs': project_vlachs
}
